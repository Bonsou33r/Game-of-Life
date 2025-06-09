#import numpy as np
import pygame as pg

gen_auto = int(input("Do you wish to create a noise-generated grid or a blank grid? Type 0 for the noise-generated grid or 1 for the blank grid: "))
while gen_auto > 1 or gen_auto < 0:
    gen_auto = int(input("The number you chose did not represent a valid option. Please type 0 or 1 to choose your grid type: "))
size = int(input("What is the size of the grid you want? Size (in pixels): "))
screen = pg.display.set_mode((size+5, size+5))
running = True

#def generate_grid():
#    if gen_auto == 0:
#def next_gen():
#generate_grid()
#next_gen()
