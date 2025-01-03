# Snake game
Made by your's truly.

If you aren't familiar with Python projects, check out [Extra notes](#extra-notes) at the bottom of this README.

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

## Controls
- **W**: Move up
- **A**: Move left
- **S**: Move down
- **D**: Move right
- **Esc**: Quit the game

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

3. **Launch the Game**: Start the game on a separate thread, using two Queues for communication—one for sending snake direction commands and another for receiving the positions of the snake and food, as shown below:
   ```python
   info_queue = Queue()
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

Note: there is an example bot included in the `bots` folder named `example bot.py`.

## How to use the queue system
The game uses a queue-based system for communication between the main game loop and bots. The main loop sends the current snake and food positions as `pygame.Rect` objects through a Queue. Bots process this data and send movement commands (0=up, 1=left, 2=down, 3=right, 4=quit, 5=pause all snakes) back through another Queue.

## Configuration
You can customize the game settings in the `settings.json` file. The settings section focuses on user preferences, while the config section deals with game parameters. Below are the available settings and their default values:

## Settings

- **name**: Player/game profile name (default: `"Joker"`)
- **screen size**: Display resolution in pixels [width, height] (default: `[640, 480]`)
- **ups**: Updates per second (default: `120`)
- **fps**: Frames per second (default: `120`)
- **color pattern length**: Number of colors in the pattern cycle (default: `5`)
- **color scheme**: Predefined color theme name (default: `"neon_cyberpunk"`)
- **color style**: Color theme variant selector (default: `1`)
- **continues colors**: Whether colors change continuously (default: `false`)
- **portals**: Enable/disable portal wrapping (default: `true`)
- **eating speeds you up**: Whether consuming food increases speed (default: `false`)
- **eating speed you up amount**: Speed increase per food consumed (default: `10`)
- **audio**: Master audio toggle (default: `true`)
- **music**: Enable/disable background music (default: `true`)
- **sfx**: Enable/disable sound effects (default: `true`)
- **master volume**: Master audio volume 0.0-1.0 (default: `1.0`)
- **music volume**: Background music volume 0.0-1.0 (default: `0.2`)
- **eating sfx volume**: Eating sound volume 0.0-1.0 (default: `0.3`)
- **lose sfx volume**: Loss sound volume 0.0-1.0 (default: `0.5`)
- **music name**: Background music track selection (default: `"random"`)
- **fullscreen**: Enable/disable fullscreen mode (default: `false`)
- **random starting position**: Enable/disable random snake spawn location (default: `false`)
- **safe random starting position**: Enable/disable safe random spawn area (default: `false`)
- **snakes count**: Number of snakes in the game (default: `1`)

## Config

- **sector size**: Grid cell dimensions in pixels [width, height] (default: `[40, 40]`)
- **step**: Movement increment per update cycle (default: `4`)
- **background color**: RGB background color value (default: `[30, 30, 30]`)
- **font family**: Font typeface selection (default: `null`)
- **font size**: Text display size in pixels (default: `32`)
- **window name**: Application window title (default: `"snake game!"`)
- **lost text**: Game over message text (default: `"You lost!"`)
- **lost color**: RGB color for loss message (default: `[255, 0, 0]`)
- **quit text**: Exit confirmation message text (default: `"You quit!"`)
- **quit color**: RGB color for quit message (default: `[0, 255, 255]`)

## ⚠️ Important Notes about Settings
- **Sector size and step** must be chosen so that sector size is divisible by step without remainder for correct movement and alignment.
- **Screen size** must be divisible by sector size without remainder to ensure proper grid alignment (width with sector width, height with sector height).
- **Step must be ≤ sector size** for proper movement within the grid.

> **These constraints are critical for proper game functionality. Incorrect values may cause visual glitches or movement issues.**

## In future updates
1. Add a setting to turn on speeding up calculations to be more efficient by changing the step and reducing the ups, once it has been cranked high enough so that the ratio between ups to step is kept and all other ratios as well.
2. Make it so that the eating speed you up setting works with multiple snakes.
1. Rewrite the implemented collision detection between snakes to look less janky. Add an extra check inside after the rect cover to see how much of the rect is covered by subtracting ones middle position with the other absolute value and then comparing it with the appropriate sector size x or y.
2. Implement AI for bot snakes.
3. Add multiplayer support over a network.
4. Introduce new game modes (e.g., timed mode, survival mode).
5. Enhance the fullscreen setting to check and calculate suitable step and ups settings for optimal playability. **<!idk what this even means!>**
2. Add a start screen, when you boot up the game it shows buttons like start and settings.
2. Maybe create a setting to safely spawn food away from snakes.



## Extra notes

- All examples in this README assume commands are run from the project root directory.
- `main.py` must be run from the project folder.

## Changelog
- v0.0.0-Beta.1: Initial release with basic snake gameplay and bot support. Date: 2025-01-03

## Feedback and Suggestions
Feel free to share your thoughts, report bugs, or suggest new features by messaging me on discord: EMILIO#0663.