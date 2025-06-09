# The plan

*Organization :*
For each level:
- First step: define the precise objective of the project part with details
- Second step: define the tools that will be useful or critical for the project
- Third step: define what code is needed and make algorithms
- Fourth step: code!

*First step*
Different levels :
First level: develop a python program that can simulate the game of life (original John Conway's rules) with some settings like zoom in, add some cells, etc...
Second level: make a Docker container in which the python program can run as an app.
Third level: make a website with the integration of the Docker container in it so that the user of the website can visit several pages with explanations of the Game of Life, its story and of course the app we made.
Fourth level: deploy this website and the Docker container on a local network so that every person connected to the local network can access and use the website.
Fifth level: deploy this website on the Internet so that anybody in the world can access this website with all its content.

*Second step*
First level:
We need Python, the latest version.
We need a package to make a grid which can be filled with dead or alive cells (NumPy). We also need to implement some functionnalities, like adding alive or dead cells by clicking on the grid (matplotlib? NiceGUI for the GUI).

*Third step*
The programmation language is Python because it is simple. The package used to create the grid is NumPy, because it is fast (written in C) but also simple (thanks to its Python syntax). The package used for the UI is NiceGUI for now, but it might change in the future.

Things to code:
We need a noise generator so that the grid can be filled automatically.
We need to implement the rules of the Game of Life. The rules are:
  - 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
  - 2. Any live cell with two or three live neighbours lives on to the next generation.
  - 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
  - 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

We need to implement functionnalities such as:
    - "click to add cells"
    - "camera zooms in/zooms out"
    - "camera mooves with arrow keys"
    - (maybe too complicated) "camera follows a formation of cells on demand"
    - (even more complicated) "automatic identification of all cell formations"
    - "create new grid"

*How to organize all of that?*
Two files, one folder:
    - one Python file for the logic (the rules of the game, the program which creates or destroys cells and which creates and stores grids into a specified directory)
    - one Python file for the GUI
    - one folder to store grids
