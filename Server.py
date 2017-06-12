""" Server code (OpenGL / OpenVR code) """

#!/bin/env python
# -*- coding: utf-8 -*-

################################################################################################################################
#							Imports								       #		
################################################################################################################################

# Needed for using PyOpenGL in the server code
from OpenGL.GL import *  
from OpenGL.GL.shaders import compileShader, compileProgram

# Needed for PyOpenGL to render things onto the Vive
from openvr.glframework.glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor

# Needed for implementing sockets on Windows for interprocess communications
import zmq

# Some other needed modules
import sys
import numpy as np
import ctypes

################################################################################################################################
#							Shader Code							       #		
################################################################################################################################

vertex_code = """
	#version 450 core
	
	layout(location = 0) in vec3 position;
	layout(location = 1) in vec3 normal;
	layout(location = 4) uniform mat4 Projection = mat4(1);
	layout(location = 8) uniform mat4 ModelView = mat4(1);
	out vec3 lightColor;
	out vec3 objectColor;
	out vec3 Normal;
	out vec3 FragPos;  
	
	void main() {
		lightColor = vec3(.8, 0.8, 0.8);
		objectColor = vec3(.7, .7, .7);
		Normal = normal;
		gl_Position = Projection * ModelView * vec4(position.x * .3, position.y * .3, position.z * .3, 1.0);
		FragPos = vec3(ModelView * vec4(position.x * .3, position.y * .3, position.z * .3, 1.0));
	}
"""

fragment_code = """\
	#version 450 core
	in vec3 lightColor;
	in vec3 objectColor;
	in vec3 Normal; 
	in vec3 FragPos;  
	out vec4 FragColor;
	void main() {
	
		vec3 norm = normalize(Normal);
		vec3 lightDir = normalize(vec3(4.1, 1.0, 5.9) - FragPos);  
		float diff = max(dot(norm, lightDir), 0.0);
		vec3 diffuse = diff * lightColor;
		
		float ambientStrength = 0.5f;
		vec3 ambient = ambientStrength * lightColor;
		vec3 result = (ambient + diffuse) * objectColor;
		FragColor = vec4(result, 1.0);
	}
"""

################################################################################################################################
#							Rendering Code							       #		
################################################################################################################################

class Actor(object):
    
	def __init__(self, vertices):
		"""
		Description: 	When first created, the object saves the vertices (including the properties of the vertices,
				such as normals) of everything to be rendered in the scene.
		Arguments:	vertices - the vertices of everything to be rendered in the scene, including the properties of
				each vertex
		Return:		Nothing.
		"""
		
		self.program = 0
		
		# Convert to numpy array - make sure to convert to float32. On 64-bit systems,
		# numpy defaults to float64, which is bad.
		self.vertices = np.array(vertices, dtype=np.float32)

	def init_gl(self):
		"""
		Description: 	Creates the shader program to be used in rendering the models in the Vive.
		Arguments:	Nothing.
		Return:		Nothing.
		"""

		# Create shaders
		self.program  = glCreateProgram()
		vertex   = glCreateShader(GL_VERTEX_SHADER)
		fragment = glCreateShader(GL_FRAGMENT_SHADER)
		
		# Indicate the source code for the shaders (see above)
		glShaderSource(vertex, vertex_code)
		glShaderSource(fragment, fragment_code)

		# Compile each of the shaders
		glCompileShader(vertex)
		glCompileShader(fragment)

		# Link the shaders together into one shader program to be used in the rendering process.
		glAttachShader(self.program, vertex)
		glAttachShader(self.program, fragment)
		glLinkProgram(self.program)

		# No longer need the shader code now that we have the program.
		glDetachShader(self.program, vertex)
		glDetachShader(self.program, fragment)

	def display_gl(self, modelview, projection):
		"""
		Description: 	Renders the models onto the Vive display using the vertex properties we had passed into the
				init function and the shader program that we had created above. 
		Arguments:	modelview - the modelview matrix to transform the model 
				projection - the projection matrix to transform the model 
		Return:		Nothing.
		"""
		
		# Indicate the shader program to use in rendering the models
		glUseProgram(self.program)
		glUniformMatrix4fv(4, 1, False, projection)
		glUniformMatrix4fv(8, 1, False, modelview)
		
		# Render using a VBO. For some reason, the element buffer array (EBO) is not working, causing the
		# program to crash. This should probably be done later so as to be more efficient
		self.vao = glGenVertexArrays(1)
		self.vbo = glGenBuffers(1)
		glBindVertexArray(self.vao)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
		glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
		
		# Vertex attribute for the vertices
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * int(self.vertices.nbytes / self.vertices.size), ctypes.c_void_p(0))
		glEnableVertexAttribArray(0)
		
		# Vertex attribute for the normals
		glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * int(self.vertices.nbytes / self.vertices.size), ctypes.c_void_p(3 * int(self.vertices.nbytes / self.vertices.size)))
		glEnableVertexAttribArray(1)
		
		# Render to the display
		glEnable(GL_DEPTH_TEST)
		glDrawArrays(GL_TRIANGLES, 0, int(self.vertices.size / 6))
		glBindVertexArray(0)
		
	def dispose_gl(self):
		"""
		Description: 	Clean up code once we're done. Not really called here - this is placed here just in case.
		Arguments:	Nothing.
		Return:		Nothing.
		"""
		
		glDeleteProgram(self.program)
		self.program = 0
		glDeleteVertexArrays(1, (self.vao,))
		self.vao = 0

################################################################################################################################
#							Main Code							       #		
################################################################################################################################

if __name__ == "__main__":

	# Create a socket and have it listening at the following port
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:5555")
	
	#  Wait for data from client - in this case the vertex data needed to render the models onto the Vive
	message = socket.recv()

	# Set up the Blender scene needed to be rendered on the display
	actor = Actor([float(a) for a in message.decode("utf-8").split()])
	renderer = OpenVrGlRenderer(actor)
	
	# Show the positions of the Vive controllers within the headset
	controllers = TrackedDevicesActor(renderer.poses)
	controllers.show_controllers_only = False
	renderer.append(controllers)
	
	# Render
	glutApp = GlutApp(renderer, b"glut OpenVR color cube")
	glutApp.run_loop()
