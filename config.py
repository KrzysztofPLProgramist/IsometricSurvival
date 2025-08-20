import pygame
from random import *
from math import *
import json
import os

pygame.init()

# screen
# WIDTH = 1920 / 4
# HEIGHT = 1080 / 4

os.environ["SDL_VIDEO_CENTERED"] = '1'
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

halfWIDTH = WIDTH / 2
halfHEIGHT = HEIGHT / 2

SCREEN_SIZE = (WIDTH, HEIGHT)
# SCREEN_SIZE = (0, 0)

SCALE = 2

# colors
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# ui colors
BG_COLOR = BLACK


# tiles
TILE_SIZE = 32



