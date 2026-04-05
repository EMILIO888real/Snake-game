# Snake game
Made by your's truly. [GitHub](https://github.com/EMILIO888real/Snake-game)

If you aren't familiar with Python projects, check out [Extra notes](#extra-notes) at the bottom of this README.

## Contents
- [Installation](#installation)
- [How to play](#how-to-play)
- [Default controls](#default-controls)
- [Configuration](#configuration)
  - [Settings](#settings)
  - [Config](#config)
  - [Extra customization](#extra-customization)
- [Extra notes](#extra-notes)
- [Warning](#warning)
- [Features](#features)
- [Feedback and Suggestions](#feedback-and-suggestions)
- [Honorable mentions](#honorable-mentions)
- [Changelog](#changelog)
- [In future updates](#in-future-updates)

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
Use wasd to move the snake around the screen. Eat the food to grow longer and gain points. Avoid running into yourself.

## Default controls
| Key | Action |
|-----|--------|
| **W** | Move up |
| **A** | Move left |
| **S** | Move down |
| **D** | Move right |
| **Q** | Quit the game |
| **ESC or SPACE** | Pause/unpause the game |
| **G** | Toggle grid lines |
| **\`** | Toggle performance stats display |
| **F** | Forward music track |
| **B** | Backward music track |
| **KP + or mouse wheel up** | Music volume up *(hold key)* |
| **KP - or mouse wheel down** | Music volume down *(hold key)* |
| **R** | Queue current song |
| **LALT + r** | Repeat current song indefinitely |
| **Y** | Restart the game |
| **U** | Toggle stopwatch |
| **Home** | Exits soft restarting mode |
| **C** | opens the settings menu |
| **KP +** | to go to the next settings page |
| **KP -** | to go to the previous settings page |
| **Z** | switch setting section key |
| **S** | apply settings key |
| **END** | crash the game |
| **F1** | enable/disable special effects |


*(hold key)*: just indicates that it is a key you can hold, not need to necessarily

## Configuration
You can customize the game settings in the `settings.json` file. The settings section focuses on user preferences, while the config section deals with game parameters. Below are the available settings and their default values:

### Settings
See [SETTINGS.md](./SETTINGS.md) for detailed information on user-configurable settings.

### Config
See [CONFIGURATION.md](./CONFIGURATION.md) for detailed information on game configuration parameters.

### Extra customization
See [CUSTOMIZATION.md](./docs/CUSTOMIZATION.md) for detailed information on how to add custom assets and important notes about settings.

## Extra notes
- If you installed the bundled version of the game you can't run a bot to play the game.
- All examples in all documentation assume commands are run from the project root directory.
- `main.py` must be run from the project folder.

## Warning
1. If you encounter any errors or problems be sure to check the terminal, in case the error handler caught it, if so please send the error report to a developer via Discord or Github.
2. On Windows, the latest Python version supported by this project is **3.12**, because `pygame` is not available on `pip` for newer versions unless you find an alternate installation method.

## Features
- Customizable settings and configuration [see details](#configuration)
- Bot support with an algorithm tester bot included [see details](./bots/BOTS.md)
- Music player with support for custom playlists and volume control
- And more!

## Feedback and Suggestions
Feel free to share your thoughts, report bugs, or suggest new features by messaging me on discord: EMILIO#0663.

## Honorable mentions
- **Copilot** for documentation and varies bot algorithm ideas, as well project structure and organization ideas.
- **ChatGPT** for theoretical explanations and ideas for algorithms and possible solutions to interesting and cool features.

## Changelog
See the full history in [CHANGELOG.md](./CHANGELOG.md).

## In future updates
see [ROADMAP.md](./docs/ROADMAP.md) for planned features and improvements.