# Snake game
Made by your's truly. [github](https://github.com/EMILIO888real/Snake-game)

If you aren't familiar with Python projects, check out [Extra notes](#extra-notes) at the bottom of this README.

## Warning
1. If you encounter any errors or problems be sure to check the terminal, in case the error handler caught it, if so please send the error report to a developer via Discord or Github
2. If you are on **windows** you should check if the `slower key inputs` setting works for your system, by default it is disabled on windows via the `compatibility` setting.
3. For **windows** users, the newest python version available for this project is **3.12**, since pygame doesn't support any version above 3.12. Unless you can find a way to install pygame for newer versions successfully.
4. If you are on **windows** and are experiencing inconsistent frame times, try changing the `busy_loop_threshold` setting to a higher value, for example `0.01`, this will make the clock bust wait more, which can help with inconsistent frame times on some systems. You can experiment with different values to find the best one for your system. For windows users, the default value is `0.001`, set via the compatibility.

## Contents
- [Installation](#installation)
- [How to play](#how-to-play)
- [Controls](#default-controls)
- [Features](#features)
- [How to Add a Bot](#how-to-add-a-bot)
- [How to use the queue system](#how-to-use-the-queue-system)
- [Configuration](#configuration)
  - [Settings](#settings)
  - [Config](#config)
  - [⚠️ Important Notes about Settings](#️-important-notes-about-settings)
- [Simple bot](#simple-bot)
  - [Simple bot settings](#simple-bot-settings)
  - [Important notes about the simple bot settings](#important-notes-about-the-simple-bot-settings)
- [In future updates](#in-future-updates)
- [Extra notes](#extra-notes)
- [Changelog](#changelog)

## Installation
1. Ensure you have Python 3.x installed on your system.
2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Before running the game cd into the project folder.
4. Run the game:
   ```bash
   python main.py
   ```

## How to play
Use wasd to move the snake around the screen. Eat the food to grow longer and gain points. Avoid running into yourself or the walls (unless portals are enabled).

## Default controls
- **W**: Move up
- **A**: Move left
- **S**: Move down
- **D**: Move right
- **Q**: Quit the game
- **ESC or SPACE**: Pause/unpause the game
- **G**: Toggle grid lines
- **~**: Toggle performance stats display
- **F**: Forward music track
- **B**: Backward music track
- **KP + or mouse wheel up**: Music volume up *(hold key)*
- **KP - or mouse wheel down**: Music volume down *(hold key)*
- **r**: Queue current song
- **LALT + r**: Repeat current song indefinitely
- **y**: Restart the game
- **u**: Toggle stopwatch
- **Home** Exits soft restarting mode

*(hold key)*: just indicates that it is a key you can hold, not need to necessarily

## Features
- Classic snake gameplay with modern twists.
- Customizable settings via `settings.json`.
- Support for AI bots through a queue-based communication system.
- Color schemes and audio options for an enhanced experience.

## How to Add a Bot
To integrate a bot into the game, follow these steps:

1. **Create a Bot File**: Create a new Python file for your bot (e.g., `my_bot.py`).

2. **Import Required Modules**:
   ```python
   from main import main
   from queue import Queue
   from threading import Thread
   ```
   *main is the main game function from `main.py`.*

3. **Launch the Game**: Start the game on a separate thread, using two Queues for communication—one for sending snake direction commands and another for receiving the positions of the snake and food, as shown below:
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

- **Info Queue** (game → bot): Sends snake and food positions as `pygame.Rect` objects, plus all game settings at startup. Also sends status codes: `-1` (user quit), `-2` (snake crashed), `-3` (game error). After the code it also sends basic stats like points and playtime time and rating for that game specifically.
- **Commands Queue** (bot → game): Receives movement commands: `0` (up), `1` (left), `2` (down), `3` (right), `4` (quit), `5` (pause all snakes), `6` (exits soft restarting mode).

Your bot reads the game state from the info queue and sends movement commands through the commands queue.

## Configuration
You can customize the game settings in the `settings.json` file. The settings section focuses on user preferences, while the config section deals with game parameters. Below are the available settings and their default values:

### Settings
See [SETTINGS.md](./SETTINGS.md) for detailed information on user-configurable settings.

### Config
See [CONFIGURATION.md](./CONFIGURATION.md) for detailed information on game configuration parameters.

### ⚠️ Important Notes about Settings
- **Sector size and step** must be chosen so that sector size is divisible by step without remainder for correct movement and alignment.
- **Screen size** must be divisible by sector size without remainder to ensure proper grid alignment (width with sector width, height with sector height).
- **Step must be ≤ sector size** for proper movement within the grid.
- **If you change the color style or color scheme setting you must delete the .colors.txt file in the CWD, to apply changes.**
- **snake bot delay setting possibly doesn't work and will most likely decrease performance. Do calculations before setting it for best compatibility!**
- **For project fonts, don't use bold/italic settings; instead, select the font variant with the desired style in its name.**

> **These constraints are critical for proper game functionality. Incorrect values may cause visual glitches or movement issues.**

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
- **If you are experiencing problems with the algorithms they seem to do very badly, it's possible that the game is running to quickly for the bot, in that case decrease the UPS of the game via the `UPS` setting, or you can also enable the `wait for bot` setting.**

## In future updates
1. Add the automatic report sending, by using the Gofile api.
1. Add a setting to the `simple bot` to be able to run multiple snake games at the same time.
1. Add a version blit to the start menu.
1. Change the writing system to use atomic writes. Create this function and add it to `et`
1. Add a way to soft restart the app, instead of importing everything and regenerating and what not, just reset some key values.
1. Add a setting to disable the GUI
1. Cook up the slowed performance show, by using another thread to create blits, only create them so often while the GUI loops, just blits the one that is available to it, use the same logic for the time display as well.
1. Flesh out the resizable mode, for the window.
1. Possibly optimize or rework the time display.
1. Possibly add `njit` from `numba` to compile parts of the game like the game's update logic.
1. Add automatic error report sending to a some kind of web server or place over the internet.
1. Add some setting for True multithreading or paralelism (Multiprocessing)
1. Add an option to see frame time, instead of just fps and ups, but also time.
2. For the raw time simply create a new text blittable separate form the performance one.
1. Add a setting to switch from using threads to using processes between tasks. Like snake logic and maybe some others as well.
2. Add a setting to change how many processes are there and which threads are running them, as well how effectively, A process can run multiple threads like grouping a process with threads, for example you have 10 snakes running, make it so that you can group them like so: 2x(1 process 5 threads), for more efficiency. Not to waste so much time on communication.
1. Add a setting to be able to display a background image, instead of being only available as a single color.
1. Fix/upgrade the safe food position's to work correctly with multiple snakes by making some quick calculations to convert all snakes topleft positions to be aligned with the grid. Or alternately maybe try using the collision detection logic to determine if the food would overlap any of the snakes.
2. Maybe revisit the position offset info send.
2. **Check out all of the old code and rewrite some logic to be cleaner** <- Ambiguous.
2. Check and maybe rework how the image asset drawing works
2. Add a way to create a more fulfilling profile, with a pfp, username, age and so on data.
3. Add some images to blit to screen, so you have more graphics.
3. Take and make some cool photos and videos of the game to display in the readme and maybe add another .md file for like an exhibit.
2. Make a function `simple_create_text_blit_`, a wrapper for the wrapper `create_text_blit`, to quickly generate simple blits, for blits that use pretty much only settings
2. Create a function to quickly create and add notifications
3. Add an option to toggle fullscreen
3. Add an option to have fonts sizes dynamic for different length's of text for example the music notification, if the name name of the song is long the font size gets decreased proportionally
3. Maybe change the logic for setting or changing the global volume
3. Change so that the all sfx or music files are in a list for easier editing. **idk what is this?**
3. Add fade in and out animations for graphics, for when booting up and shutdowning the game.
2. Add more sfx for: changing direction, pressing a key, like toggle grid, moving and as well for animation fade in and out audios.
2. Add some options to generate settings based on some questions and as well create some presets.
1. Make a program or function to quickly generate settings and easily able to add new text.
2. Add an option to display time, lowest as a highscore, essentially add all kinds of time related data.
2. **Calculate and correct time**, when paused pause the time should pause as well.
2. Change the duplicate nature of the code that handles movement assignment (keyboard detection, receiver code and start menu <- Could just remove the one right now and replace it with a new fresh looking one.)
3. Change the points to be individual for each snake.
3. Possibly revisit collision between snakes to rework it.
2. Implement AI for bot snakes.
3. Add multiplayer support over a network.
4. Introduce new game modes (e.g., timed mode, survival mode, battle royale, pvp in varies formats solo, duo, and so on.).
2. Add a start screen, when you boot up the game it shows buttons like start and settings.
2. possibly revisit the setting that safely spawn food away from snakes.
3. Maybe create a logger or activities archiver or something. Like for example it would save when and which snake ate food, possibly location. So you can possibly essentially record and replay a match as well for debugging and other purposes.

## Extra notes
- All examples in this README assume commands are run from the project root directory.
- `main.py` must be run from the project folder.

## Changelog
See the full history in [CHANGELOG.md](./CHANGELOG.md).

## Feedback and Suggestions
Feel free to share your thoughts, report bugs, or suggest new features by messaging me on discord: EMILIO#0663.

## Honorable mentions
- **Copilot** for documentation and varies bot algorithm ideas, as well project structure and organization ideas.
- **ChatGPT** for theoretical explanations and ideas for algorithms and possible solutions to interesting and cool features.