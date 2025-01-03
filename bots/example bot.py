from pathlib import Path
from threading import Thread
from queue import Queue
from random import randint
from sys import path
from time import sleep

path.append(str(Path('.').absolute()))

from main import main

info_queues = [Queue() for _ in range(10)]
command_queue = Queue()

Thread(target=main, daemon=True, args=[info_queues, command_queue]).start()

# Bot's logic

snake_index = 1 # That's the index of the snake being controlled rn
info_queue = info_queues[snake_index]
game_running = True
while game_running:
    info = info_queue.get()
    print(info) # gets the location of the snake and food's position
    # if info == -1:
    #     game_running = False
    for i in range(10):
        command_queue.put([i, randint(0, 3)]) # Chooses a random move
    sleep(0.001)