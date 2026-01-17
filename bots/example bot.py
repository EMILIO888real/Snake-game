from pathlib import Path
from threading import Thread
from queue import Queue
from random import randint
from sys import path
from pprint import pprint

path.append(str(Path('.').absolute()))

from main import main

SNAKE_INDEX = 0 # That's the index of the snake being controlled rn
SNAKES_COUNT = 10

info_queues = [Queue() for _ in range(SNAKES_COUNT)]
command_queue = Queue()

Thread(target=main, args=[info_queues, command_queue]).start()

info_queue = info_queues[SNAKE_INDEX]
settings = info_queue.get() # First response contains all of the running sessions settings
print('Settings:\n')
pprint(settings)

# Bot's logic

game_running = True
while game_running:
    info = info_queue.get() # gets the location of the snake and food's position as well occasional codes for the game / bot state
    if info == -1 or info == -2: # -2 is the code that means the snake crashed. and -1 means the game has been left
        game_running = False
        print('\nQuit game!' if info == -1 else '\nSnake crashed!')
    else:
        print(info)
    command_queue.put([SNAKE_INDEX, randint(0, 3)]) # Chooses a random move