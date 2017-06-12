<bold> Prerequisites </bold>

This project mostly requires knowledge of OpenGL 3 (PyOpenGL), OpenVR (PyOpenVR), and the Blender/Python API. The Blender/Python API is used to get data about the model from Blender (and to update Blender), and OpenGL is then used to tell OpenVR what to render to the Vive display. Although not implemented yet, OpenVR is also used to get the controller coordinates from the Vive, and then these coordinates would then be used to update Blender.

<bold> Previous Bugs and Fixes </bold>

The current design of the software is rather unintuitive due to several problems encountered over the course of the term. One main issue encountered was that Blender would freeze when either a window or an OpenGL context was created within Blender. The former was fixed by using torn off windows. However, it didn’t fix the latter problem. 

As a result, to fix both problems, sockets were used for interprocess communications. In this case, the OpenGL/OpenVR code was separated from the Blender python code into a separate process. The Blender python code would act as a “Client” while the OpenGL/OpenVR code would act as a “Server.” The Blender python code would send model data to the OpenGL/OpenVR code, which will then render the model onto the Vive display. Although not implemented yet, this should also work the other direction, from OpenGL/OpenVR code to Blender – this would allow user interaction with the model from the Vive.

<bold> Current Model </bold>

So the current software model is something like the following:
Blender/Python API (Client)      <-->    ZeroMQ (Socket Implementation)       <-->      OpenVR/OpenGL (Server)      <-->                                                 Vive Controllers/Display

<bold> Current Concerns </bold>

Using sockets may or may not cause issues with execution speed. Currently the data passed over TCP is small in volume. Problems may occur when the scale of the data increases. 

In addition, there seems to be a blinking problem on the Vive display when the program executes. It is unknown whether this is due to the sensors or to the code.

<bold> How to Run the Current Program </bold>

Use Windows. Use Pip to install the following. It’s recommended to install using .whl files from www.lfd.uci.edu/~gohlke/pythonlibs/. 

Make sure PyOpenGL, PyOpenVR, and ZeroMQ are installed in Blender’s Python directory. Blender’s Python interface uses the Python version that comes installed with Blender, not the Python version installed on the system. As a result, also make sure to install for the correct Python version – Blender’s python version is usually behind the most recent update. If using a 64-bit system, make sure to check PyOpenVR’s issues log for PyOpenVR.

Run Server.py using the following command: python Server.py.

Run Client.py from within the provided text editor in Blender.
