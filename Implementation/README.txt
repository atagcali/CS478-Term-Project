CS478 Term Project - Spring 2022-2023
Burak Ozturk - Alp Tugrul Agcali

1. How to install and the run the program

Our project is implemented in Python as three separate files. Thus they are normal, click-and-run Python scripts. No libraries are used that are not built-in Python / installed with pip etc.

2. User interfaces

For the Flipping Algorithm and the Randomized Incremental Algorithm, inputs for random point count and delay length between steps are through the console. Then Tkinter canvas is used to present the algorithms.

For the Fortune's Algorithm, there is a GUI for adding points to the canvas with the left-click and after adding some number of points, right-click does the triangulation. Alternatively, top bar can be used to insert some number of random points. Middle-click clears the point on the canvas. Also console reports coordinates of the points.