# Bots
This section provides information on how to create and integrate bots into the snake game. Bots can be used for various purposes, such as testing algorithms, creating AI opponents, or automating gameplay.

## How to Add a Bot
To integrate a bot into the game, follow these steps:

1. **Create a Bot File**: Create a new Python file for your bot (e.g., `my_bot.py`).

2. **Import Required Modules**:
   ```python
   from main import main
   from queue import Queue
   from threading import Thread
   ```
   *Note: `main` is the main game function from `main.py`. You can also use `multiprocessing.Queue`, but enable the `serialize data` setting.*

3. **Launch the Game**: Start the game on a separate thread or process, using two Queues for communication—one for sending snake direction commands and another for receiving the positions of the snake and food, as shown below:
   ```python
   info_queue = [Queue()]
   commands_queue = Queue()
   game_thread = Thread(target=main, args=(info_queue, commands_queue))
   game_thread.start()
   ```
You can also do it in reverse: launch your bot on a separate thread and the game on the main thread. Might be more stable that way. To learn about queues, read the ["How to use the queue system"](#how-to-use-the-queue-system) section below.

4. **Implement Bot Logic**: Write your bot logic to read the game state from the Queue and send movement commands.

5. **Run Your Bot**: Execute your bot script:
   ```bash
   python my_bot.py
   ```

Note: there is an example bot included in the `bots` folder named `example bot.py`. Also an algorithm launcher / tester called `simple bot.py`

## How to use the queue system
The game uses a queue-based system for communication between the main game loop and bots:

- **Info Queue** (game → bot): Sends snake and food positions as `pygame.Rect` objects, plus all game settings at startup. Also sends status codes: `-1` (user quit), `-2` (snake crashed), `-3` (game error). After the code it also sends basic stats like points and playtime time and rating for that game specifically. If 
- **Commands Queue** (bot → game): Receives movement commands: `0` (up), `1` (left), `2` (down), `3` (right), `4` (quit), `5` (pause all snakes), `6` (exits soft restarting mode).

Your bot reads the game state from the info queue and sends movement commands through the commands queue.

## Simple bot
There is a simple bot included in the `bots` folder named `simple bot.py`, it is a simple algorithm launcher and tester, where you can see and check out how to utilize the queue system, and also test out some simple algorithms, relies on the algorithms in the `algorithms.py` file. You can also use it to test out your own algorithms, by importing them into the `algorithms.py` file and then launching them from the `simple bot.py` file. It also comes with settings that you can change to change how the bot performs.

### Simple bot settings
- **presentation mode**: Enable/disable presentation mode for visual display (default: `true`)
- **bot runs**: Number of bot runs to execute (default: `6`)
- **sequentially**: Run algorithms sequentially or randomly (default: `true`)
- **write settings**: Save bot settings to file (default: `false`)
- **snake index**: Index of the snake controlled by the bot (default: `0`)
- **snake count**: Number of snakes for bot testing (default: `1`)
- **verbose**: Enable/disable verbose output during bot runs (default: `true`)
- **write runs**: Save each run's basic stats (default: `false`)
- **write play times**: Save each run's play time (default: `false`)
- **ups**: Updates per second for the game itself (default: `800`)

### Important notes about the simple bot settings
- **If you are experiencing problems with the algorithms they seem to do very badly, it's possible that the game is running too quickly for the bot, in that case decrease the UPS of the game via the `UPS` setting, or you can also enable the `wait for bot` setting.**