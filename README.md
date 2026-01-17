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

Note: there is an example bot included in the `bots` folder named `example bot.py`.

## How to use the queue system
The game uses a queue-based system for communication between the main game loop and bots:

- **Info Queue** (game → bot): Receives the current snake and food positions as `pygame.Rect` objects, along with all game settings sent at startup.
- **Commands Queue** (bot → game): Sends movement commands where 0=up, 1=left, 2=down, 3=right, 4=quit, 5=pause all snakes.

Your bot reads the game state from the info queue and sends movement commands through the commands queue.

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
- **grid lines**: Enable/disable grid lines (default: `true`)
- **grid lines color**: RGB color for grid lines (default: `[40, 40, 40]`)
- **cycle food colors**: Enable/disable cycling food colors (default: `true`)
- **last piece becomes food color**: Whether the last piece becomes the food color (default: `true`)
- **food starting color**: Starting color index for food (default: `1`)
- **snake starting color**: Starting color index for snake (default: `0`)
- **playlist**: Enable/disable music playlist (default: `true`)
- **sequential playlist**: Enable/disable sequential playlist (default: `false`)
- **careful between snakes collision detection**: Enable/disable careful collision detection between snakes (default: `false`)
- **borderless**: Enable/disable borderless window mode (default: `false`)

## Config

- **sector size**: Grid cell dimensions in pixels [width, height] (default: `[40, 40]`)
- **step**: Movement increment per update cycle (default: `4`)
- **increase jumps with increasing ups**: Whether jumps increase with UPS changes (default: `false`)
- **background color**: RGB background color value (default: `[30, 30, 30]`)
- **font family**: Font typeface selection (default: `null`)
- **font size**: Text display size in pixels (default: `32`)
- **font bold**: Font weight toggle (default: `null`)
- **font italic**: Font style toggle (default: `null`)
- **window name**: Application window title (default: `"snake game!"`)
- **lost text**: Game over message text (default: `"Everyone crashed!"`)
- **lost text color**: RGB color for loss message (default: `[255, 0, 0]`)
- **lost text font**: Font for loss message (default: `null`)
- **lost text font size**: Font size for loss message (default: `null`)
- **lost text bold**: Bold toggle for loss message (default: `null`)
- **lost text italic**: Italic toggle for loss message (default: `null`)
- **quit text**: Exit confirmation message text (default: `"You quit!"`)
- **quit text color**: RGB color for quit message (default: `[0, 255, 255]`)
- **quit text font**: Font for quit message (default: `null`)
- **quit text font size**: Font size for quit message (default: `null`)
- **quit text bold**: Bold toggle for quit message (default: `null`)
- **quit text italic**: Italic toggle for quit message (default: `null`)
- **bye text position**: End screen text position as relative to the screen size (default: `[0.5, 0.1]`)
- **end screen points text**: Points label text (default: `"points: "`)
- **end screen points text variable index**: Variable index for points display (default: `8`)
- **end screen points text color**: RGB color for points text (default: `[127, 0, 255]`)
- **end screen points text font**: Font for points text (default: `null`)
- **end screen points text font size**: Font size for points text (default: `null`)
- **end screen points text bold**: Bold toggle for points text (default: `null`)
- **end screen points text italic**: Italic toggle for points text (default: `null`)
- **end screen points text position**: Points text position as relative to the screen size (default: `[0.5, 0.15]`)
- **end screen high score text**: High score label text (default: `"high score: "`)
- **end screen high score text variable index**: Variable index for high score display (default: `12`)
- **end screen high score text color**: RGB color for high score text (default: `[255, 127, 0]`)
- **end screen high score text font**: Font for high score text (default: `null`)
- **end screen high score text font size**: Font size for high score text (default: `null`)
- **end screen high score text bold**: Bold toggle for high score text (default: `null`)
- **end screen high score text italic**: Italic toggle for high score text (default: `null`)
- **end screen high score text position**: High score text position as relative to the screen size (default: `[0.5, 0.2]`)
- **points text**: Points display label (default: `"points: "`)
- **points text variable index**: Variable index for in-game points (default: `8`)
- **points text color**: RGB color for points display (default: `[200, 200, 200]`)
- **points text font**: Font for points display (default: `null`)
- **points text font size**: Font size for points display (default: `null`)
- **points text bold**: Bold toggle for points display (default: `null`)
- **points text italic**: Italic toggle for points display (default: `null`)
- **points text position**: Points display position as relative to the screen size (default: `[0.9, 0.05]`)
- **start menu text**: Start menu instruction text (default: `"Press any of the movement(WASD) keys to start"`)
- **start menu text color**: RGB color for start menu text (default: `[255, 255, 255]`)
- **start menu text font**: Font for start menu text (default: `null`)
- **start menu text font size**: Font size for start menu text (default: `null`)
- **start menu text bold**: Bold toggle for start menu text (default: `null`)
- **start menu text italic**: Italic toggle for start menu text (default: `null`)
- **start menu text position**: Start menu text position as relative to the screen size (default: `[0.5, 0.45]`)
- **paused text**: Pause screen message text (default: `"Game paused"`)
- **paused text color**: RGB color for paused message (default: `[255, 255, 0]`)
- **paused text font**: Font for paused message (default: `null`)
- **paused text font size**: Font size for paused message (default: `null`)
- **paused text bold**: Bold toggle for paused message (default: `null`)
- **paused text italic**: Italic toggle for paused message (default: `null`)
- **paused text position**: Paused text position as relative to the screen size (default: `[0.5, 0.45]`)
- **snake bot delay**: Delay for bot snakes in seconds (default: `0.0`)
- **collision between snakes**: Enable/disable snake-to-snake collision (default: `true`)
- **eating sfx**: Eating sound effect filename (default: `"eating.mp3"`)
- **lose sfx**: Loss sound effect filename or selection mode (default: `"random"`)
- **music fade out**: Music fade-out duration in milliseconds (default: `2000`)
- **sequential starting position**: Whether snakes spawn sequentially (default: `false`)
- **careful between snakes collision x portion**: Snake collision detection X sensitivity (default: `0.5`)
- **careful between snakes collision y portion**: Snake collision detection Y sensitivity (default: `0.5`)

## ⚠️ Important Notes about Settings
- **Sector size and step** must be chosen so that sector size is divisible by step without remainder for correct movement and alignment.
- **Screen size** must be divisible by sector size without remainder to ensure proper grid alignment (width with sector width, height with sector height).
- **Step must be ≤ sector size** for proper movement within the grid.
- **If you change the color style or color scheme setting you must delete the .colors.txt file in the CWD, to apply changes.**
- **snake bot delay setting possibly doesn't work and will most likely decrease performance. Do calculations before setting it for best compatibility!**

> **These constraints are critical for proper game functionality. Incorrect values may cause visual glitches or movement issues.**

## In future updates
1. Make some kind of visual distinguishable feature for the head.
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
2. Maybe create a setting to safely spawn food away from snakes.
3. Maybe create a logger or activities archiver or something. Like for example it would save when and which snake ate food, possibly location. So you can possibly essentially record and replay a match as well for debugging and other purposes.

## Extra notes

- All examples in this README assume commands are run from the project root directory.
- `main.py` must be run from the project folder.

## Changelog
- v0.0.0-Beta.1: Initial release with basic snake gameplay and bot support. Date: 2026-01-03
- v0.0.0-Beta.1.9 Right before second beta, almost all of the features, just some changes from the survey will differ Beta.2 and Beta.1.9. Date: 2026-01-17

## Feedback and Suggestions
Feel free to share your thoughts, report bugs, or suggest new features by messaging me on discord: EMILIO#0663.

## Honorable mentions
- **Snuffa** for relatively active testing.