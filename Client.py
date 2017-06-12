""" Client code (Blender Python API code) """

#!/bin/env python
# -*- coding: utf-8 -*-

# Needed for implementing sockets for interprocess communications
import zmq

# Needed for talking with the Blender software
import bpy
import string

# Create a socket to talk to server on the same port
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Access the active object in the Blender interface. Error checking has not been implemented here. In addition, need to change
# this to loop over all objects in the scene to get all vertices that needed to be rendered.
me = bpy.context.active_object.data

# Obtain model data in the form of quadrilaterals and triangles - this is how Blender stores its models. A model is stored as an
# array of tessfaces. Each tessface has an array of vertices. If the array is of length four, it's a quadrilateral. Otherwise,
# it is a triangle. 
me.calc_tessface()

# Store vertex data into an array to be sent over to the server
vertices = []
for i in range(len(me.tessfaces)):
	
	# If the corresponding tessface is a triangle, just store each vertex and its corresponding normal (for that face).
	# A vertex can have multiple normals associated with it, the number of which depends on the number of faces the vertex
	# is part of. The normals will be used to 
	if len(me.tessfaces[i].vertices) == 3:
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y) 
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.y)
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])				
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y) 
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])				
		
	# If the corresponding tessface is a quad, since you need to pass in triangles to OpenGL, convert the quads into
	# triangles. For a quad, the vertices are given in the following order - the first three vertices make up one triangle,
	# and the first, third, and fourth vertices make up another triangle.
	else:
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y)
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])				
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[1]].co.y) 
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y)
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])
		
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[0]].co.y)
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[2]].co.y) 
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])
		vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.x) 
		vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.z)
		vertices.append(me.vertices[me.tessfaces[i].vertices[3]].co.y) 		
		vertices.append(me.tessfaces[i].normal[0])
		vertices.append(me.tessfaces[i].normal[2])
		vertices.append(me.tessfaces[i].normal[1])

# Convert to appropriate format to send over the socket to the server - there may be a more efficient method to do this
vertices = ''.join(str(e) + ' ' for e in vertices)
socket.send(bytes(vertices, 'utf-8'))
