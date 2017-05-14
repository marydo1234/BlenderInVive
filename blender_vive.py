"""
This application is a rough draft for the interface between Blender3D and HTC Vive.
The code is messy and unorganized. However, that will be remedied as I go. 

TODOs:

	1. Expand from model to scene view. Should be quick, but right now, only the 
	   active object is displayed on the Vive.
	2. Controller interactions.
	3. Menus and passing commands between controllers and the Vive.
	4. Textures and fancier display techniques.
	5. Animation.
	
Author: Mary Do

"""

#!/bin/env python
# -*- coding: utf-8 -*-

from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from openvr.glframework.glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor


import bpy
import sys
import numpy as np
import ctypes

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

class Actor(object):
    
	def __init__(self):
		self.program = 0

	def init_gl(self):
	
		# Store vertices into arrays
		me = bpy.context.active_object.data
		me.calc_tessface()
		self.vertices = []
		
		# TODO: Loop through all objects in scene in order to display everything.
		for i in range(len(me.tessfaces)):
			if len(me.tessfaces[i].vertices) == 3:
			
				# Vertices making up a triangular surface and
				# The normal to this surface - will be used to calculate lighting
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y) 
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.y)
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])				
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y) 
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])				
				
			else:
			
				# Vertices making up the triangular surfaces that make up the quad
				# and the normal to this surface - will be used to calculate lighting
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y)
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])				
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.y) 
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y)
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y)
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y) 
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.x) 
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.z)
				self.vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.y) 		
				self.vertices.append(me.tessfaces[i].normal[0])
				self.vertices.append(me.tessfaces[i].normal[2])
				self.vertices.append(me.tessfaces[i].normal[1])
				
		# Convert to numpy array - make sure to convert to float32. On 64-bit systems,
		# numpy defaults to float64, which is bad.
		self.vertices = np.array(self.vertices, dtype=np.float32)

		# Create shaders
		self.program  = glCreateProgram()
		vertex   = glCreateShader(GL_VERTEX_SHADER)
		fragment = glCreateShader(GL_FRAGMENT_SHADER)
		
		glShaderSource(vertex, vertex_code)
		glShaderSource(fragment, fragment_code)

		glCompileShader(vertex)
		glCompileShader(fragment)

		glAttachShader(self.program, vertex)
		glAttachShader(self.program, fragment)

		glLinkProgram(self.program)

		glDetachShader(self.program, vertex)
		glDetachShader(self.program, fragment)

	def display_gl(self, modelview, projection):
		glUseProgram(self.program)
		glUniformMatrix4fv(4, 1, False, projection)
		glUniformMatrix4fv(8, 1, False, modelview)
		
		# Render using a VBO
		
		# TODO: For some reason, the element buffer array (EBO) is not working, causing the
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
		
		glEnable(GL_DEPTH_TEST)
		glDrawArrays(GL_TRIANGLES, 0, int(self.vertices.size / 6))
		glBindVertexArray(0)
		
	def dispose_gl(self):
		glDeleteProgram(self.program)
		self.program = 0
		glDeleteVertexArrays(1, (self.vao,))
		self.vao = 0

		
if __name__ == "__main__":

	actor = Actor()
	renderer = OpenVrGlRenderer(actor)
	controllers = TrackedDevicesActor(renderer.poses)
	controllers.show_controllers_only = False
	renderer.append(controllers)
	with GlutApp(renderer, b"glut OpenVR color cube") as glutApp:
		glutApp.run_loop()