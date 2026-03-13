''' This is an example and a clean documented bot that can run and test different algorithms.
You can make your own bot using this as a template, or just use it to test out the available algorithms.
You can also add your own algorithm to the list of presets and use it in the bot's logic.
'''

from pathlib import Path
from multiprocessing import Process, Queue
from sys import path
from json import dump, load
from statistics import mean
from algoritms import vector_based, simple_bot, greedy, randomized, greedy_safe_move, combined_algorithm
from random import randint
from json import dumps
from datetime import datetime
from time import perf_counter

path.append(str(Path('.').absolute()))

from main import main
from custom_modules.ege import tuple_to_rect # tuple to rect is in custom modules folder and used for deserializing received data
from custom_modules.et import print_colored_text, read_json, merge_settings, clear_lines, hide_cursor, show_cursor, format_time

bot_default_settings = read_json(Path('bots/.default bot settings.json'))
bot_user_settings = read_json(Path('bots/bot settings.json'))

bot_settings = merge_settings(bot_user_settings, bot_default_settings)


ALL_PRESETS = [vector_based, simple_bot, greedy, randomized, greedy_safe_move, combined_algorithm] # List of all available algorithms. You can add your own algorithm here and use it in the bot's logic.


presentation_mode = bot_settings['presentation mode'] # If you want a clean demonstration
bot_runs = bot_settings['bot runs']
sequentially = bot_settings['sequentially']
if bot_runs > len(ALL_PRESETS):
    sequentially = False
verbose = bot_settings['verbose']

snake_index = bot_settings['snake index'] # That's the index of the snake being controlled rn
snakes_count = bot_settings['snake count'] # Total number of snakes in the game. Just for sanity checks and to know how many queues we need.

# Creates the text file, just in case the user hasn't launched the game ever.
if not Path('settings.json').exists():
    with open('settings.json', 'w') as f:
        f.write('{"name": "simple bot"}')

# Reads from our settings file
with open('settings.json', 'r') as f:
    user_settings: dict = load(f)

required_settings = {'serialize data': True} # Need to serialize data if you are using processes.           Might work without, but isn't recommended.

# Makes the game easy to run quickly multiple times
recommended_settings = {'ups': 'max speed', # Makes the game run fast
                        'start direction': 0, # Predictable start, otherwise we would have to check 2 different snake positions to tell us which way the snake is facing. Since default is random (4)
                        'wait for bot': True, # Waits for the bot to send the move command before updating the game state. Nice setting for running a bot fast and not having to worry about the game updating before the bot can react.
                        'disable key inputs': True, # Disables key inputs so they don't interfere with the bot's commands. Not required, but recommended if you don't want to accidentally mess up the bot's performance by pressing keys.
                        'show performance stats': False, # Since the game is running at a very high speed, the performance stats can be distracting and aren't really needed. You can still enable them if you want to see how the game is performing at such high speeds.
                        'GUI': False, # Disables the GUI, so the game runs even faster and doesn't consume resources on rendering. Not required, but recommended if you want to run the bot at very high speeds and don't care about visually seeing the game. You can still enable it if you want to see the game while the bot is playing.
                        'soft restart': True, # Instead of fully quitting and relaunching the game for each run, which can take a lot of time, we can just reset the game state and keep the process running. This is much faster. Experimental feature.
                        "step": 20 # Set it to 20, since each sector is 20x20, makes it jump the whole sector at a time, which is nice for the bot's performance.
                        }

# Use these preference settings no matter if in presentation mode or not
highly_recommended_settings = {'skip start menu': True, # Skip so the user doesn't have to interact
                               'skip end screen': True, # Skip so the user doesn't have to interact
                               'name': 'simple*bot!', # User profile set to a bot
                               'ups': bot_settings['ups'], # Makes the game run fast, but not too fast so we can still see what's going on
                               'audio': False, # Turns off audio
                               'sector size': [20, 20], # Makes the scaling much smaller for a bigger field, so there is more space for the snake to move around and the bot can perform better. Also makes it easier to visually track the snake's movement.
                               'show time': False, # Hides the time display, since it can be distracting and isn't really needed when the game is running at a high speed.
                               'show performance stats': True, # Enables from the start performance display. Just in case pc can't reach set speed.
                               } 

# add some user settings before starting our bot
required_settings.update(user_settings)
required_settings.update(highly_recommended_settings)
if not presentation_mode:
    required_settings.update(recommended_settings)

# Writes them
with open('settings.json', 'w') as f:
    dump(required_settings, f, indent=4)

def run_bot():

    global move_direction

    # Bot's logic

    while True:
        info = info_queue.get() # gets the location of the snake and food's position as well occasional codes for the game / bot state
        
        if type(info) != dict: # Status codes for the game state. -1 means the game was quit, -2 means the game process crashed, -3 means the game encountered an error. In all of these cases we want to stop the bot and relaunch the game.
            if verbose:
                match info:
                    case -1:
                        print_colored_text('Quit game!', [0, 255, 0])
                    case -2:
                        print_colored_text('Crashed!', [0, 0, 255])
                    case -3:
                        print_colored_text('Game encountered an error!', [255, 0, 0])
            if not settings['soft restart']:
                game_process.join() # waits for the game to fully quit and release all it's resources before relaunching it.
            break
        else:
            snake_pos = [tuple_to_rect(pos) for pos in info['snake position']]
            food_pos = tuple_to_rect(info['food position'])

        # Bot's thinking. Just one of the algorithms

        move_direction = chosen_algorithm(snake_pos, food_pos) # Get the move direction from the algorithm. 0=up, 1=left, 2=down, 3=right
        
        command_queue.put([snake_index, move_direction]) # Send move command: [snake index, direction (0=up, 1=left, 2=down, 3=right)]

def expr():
    return i < (len(ALL_PRESETS) if presentation_mode else bot_runs) # Simple expression to evaluate whether to keep testing. This one runs the bot 5 times.


if __name__ == '__main__': # Required when using processes (entry point)
    with open(Path('bots/scores.txt'), 'w') as f:
        f.write('')

    scores = []
    play_times = []

    testing_time_start = datetime.now()
    if not verbose:
        start_time = perf_counter() # Just for measuring the time it takes to run a single game, to give the user an estimate of how long the testing will take.
        hide_cursor()
        time_left_width = len(str(bot_runs)) * 2

    first_time_launch = True
    i = 0 # for the expr
    while expr():

        if first_time_launch:
            # Create queues for inter-process communication
            info_queues = [Queue() for _ in range(snakes_count)]
            command_queue = Queue()

            # Launches the game in a separate process, and passes the queues to it so it can send info to the bot and receive commands from it.
            game_process = Process(target=main, args=[info_queues, command_queue])
            game_process.start()

            info_queue = info_queues[snake_index]

            if not presentation_mode:
                first_time_launch = False

        settings = info_queue.get() # First response contains all of the running sessions settings

        move_direction = settings['start direction'] # Initialize move direction to avoid moving opposite at game start
        chosen_algorithm = ALL_PRESETS[i if sequentially else randint(0, len(ALL_PRESETS) - 1)] # Change this to change the bot's algorithm. Available presets: vector_based, simple_bot, greedy, randomized. You can also make your own algorithm and use it here.
            
        if verbose:
            print('Chosen algorithm:', chosen_algorithm.__name__)
        else:
            print_colored_text(f'estimated time left: {format_time(round((perf_counter() - start_time) * (bot_runs - i) / (i + 1), 2))} | Runs left: {str(bot_runs - i - 1)}/{bot_runs:<{time_left_width}}', flush=True, end='\r') # Gives the user an estimate of how long the testing will take based on the time it took to run the current game and how many games are left.

        run_bot()
        i += 1

        save = info_queue.get()

        scores.append((chosen_algorithm.__name__, save['score']))
        play_times.append(save['play time'])
    else:
        # Sends the signal to quit soft restart mode, 6 and then to quit the program 4
        if settings['soft restart']:
            command_queue.put((0, 6))
            command_queue.put(((0, 4)))

        if not verbose: # Clean up the non verbose time estimate
            clear_lines()
            show_cursor()

        # writes the scores text file
        with open(Path('bots/scores.txt'), 'a') as f:
            i = 0 # for the same expr

            # Just writes all the scores in a nice format.
            if bot_settings['write runs']:
                f.write('All attempts:\n')
                while expr():
                    f.write(f'[{scores[i][0]}] attempt: {i}. Score: {scores[i][1]}\n')
                    i += 1
            
            total_time = datetime.now() - testing_time_start
            f.write(f'\nTotal time: {total_time}\nAverage time per game: {round(total_time.total_seconds() / bot_runs, 2)} seconds')

            # Some statistics about the scores
            lowest_score = min(scores, key=lambda x:x[1])
            highest_score = max(scores, key=lambda x:x[1])
            f.write(f'\n\nSome statistics:\n\tAverage score: {round(mean([i[1] for i in scores]), 2)}\n\tLowest score: {lowest_score[1]} [{lowest_score[0]}]\n\tHighest score: {highest_score[1]} [{highest_score[0]}]\n\tAll together score: {sum([i[1] for i in scores])}')

            if bot_settings['write play times']:
                f.write('\n\n\tPlay times:')
                for play_time_i in range(len(play_times)):
                    f.write(f'\n\t\t{scores[play_time_i][0]}: {play_times[play_time_i]} seconds')
                f.write(f'\n\n\t\tAverage play time: {round(mean(play_times), 2)} seconds\n\t\tTotal play time: {round(sum(play_times), 2)} seconds\n\t\tFastest play time: {round(min(play_times), 2)} seconds\n\t\tSlowest play time: {round(max(play_times), 2)} seconds')

            # Algorithm performance comparison
            f.write('\n\n\tTotal runs:')
            for algorithm in ALL_PRESETS:
                check_algorithm = algorithm.__name__
                f.write(f'\n\t\t{check_algorithm}: {len([score for score in scores if score[0] == check_algorithm])}')

            # Writes each algorithm's performance statistics, like highest score, lowest score and average score.
            # determines which algorithm had the highest single score and which one had the highest average score.
            highest_algorithm_scores = []
            lowest_algorithm_scores = []
            average_algorithm_scores = []

            for algorithm in ALL_PRESETS:
                algorithm = algorithm.__name__

                if any(score[0] == algorithm for score in scores):
                    highest_algorithm_scores.append(max([score for score in scores if score[0] == algorithm]))
                    lowest_algorithm_scores.append(min([score for score in scores if score[0] == algorithm]))
                    average_algorithm_scores.append((algorithm, round(mean([score[1] for score in scores if score[0] == algorithm]), 2)))

            for i in range(len(highest_algorithm_scores)):
                f.write(f'\n\n\t{highest_algorithm_scores[i][0]}:\n\t\tHighest score: {highest_algorithm_scores[i][1]}\n\t\tLowest score: {lowest_algorithm_scores[i][1]}\n\t\tAverage score: {average_algorithm_scores[i][1]}')

            highest_algorithm_scores.sort(key=lambda x:x[1], reverse=True)
            lowest_algorithm_scores.sort(key=lambda x:x[1])
            average_algorithm_scores.sort(key=lambda x:x[1], reverse=True)

            # Highlights the best performing algorithm and the most consistent algorithm (highest average score) in the overall statistics.
            f.write(f'\n\n\tBest algorithm: {highest_algorithm_scores[0][0]} [highest of all scores]\n\tMost consistent algorithm: {average_algorithm_scores[0][0]} [highest average score]\n\tWorst algorithm: {lowest_algorithm_scores[0][0]} [lowest of all scores]\n\tLeast consistent algorithm: {average_algorithm_scores[-1][0]} [lowest average score]')
            
            f.write('\n\n\tAlgorithm rankings [highest score]:')
            for highest_score in highest_algorithm_scores:
                f.write(f'\n\t\t{highest_score[0]}: {highest_score[1]}')
            
            f.write('\n\n\tAlgorithm rankings [average score]:')
            for average_score in average_algorithm_scores:
                f.write(f'\n\t\t{average_score[0]}: {average_score[1]}')

            if bot_settings['write settings']:
                f.write(f'\n\nSettings: {dumps(settings, indent=4)}')

        # Reset the user setting to the original
        with open('settings.json', 'w') as f:
            dump(user_settings, f, indent=4)

        # Final message to the user, with a reminder of where to find the scores and how long the testing took.
        print_colored_text(f'Finished running bot!', [0, 255, 0])
        print(f'You can check out all of the scores here: {Path('./bots/score.txt')}')
        print_colored_text(f'Full total time: {datetime.now() - testing_time_start}')
