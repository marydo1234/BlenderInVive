import zmq
import bpy
import string


context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Store vertices into arrays
me = bpy.context.active_object.data
me.calc_tessface()
vertices = []

# TODO: Loop through all objects in scene in order to display everything.
for i in range(len(me.tessfaces)):
	if len(me.tessfaces[i].vertices) == 3:
	
		# Vertices making up a triangular surface and
		# The normal to this surface - will be used to calculate lighting
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
		
	else:
	
		# Vertices making up the triangular surfaces that make up the quad
		# and the normal to this surface - will be used to calculate lighting
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

vertices = ''.join(str(e) + ' ' for e in vertices)

socket.send(bytes(vertices, 'utf-8'))
