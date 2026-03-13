'''
Snake game made in python with pygame. Made by your's truly. Check README.md for more info and instructions. If you want to contribute, report a bug, or just want to chat about the game check out the github repo, links in the README.md!
'''

from datetime import datetime, timedelta

import_time = datetime.now()

import pygame
import sys # So we can access the exception hook
import threading
from random import randint
from itertools import cycle
from pathlib import Path
from json import load, dump
from queue import Queue
from typing import Any, Callable, Optional, Sequence
from time import perf_counter, sleep
from os import fsync, listdir, _exit
from decimal import Decimal
from traceback import print_exception, format_exception

# from numba import njit # Add this later for some extra performance. Might not be possible due to new and well made syntax

from custom_modules.et import color_generator, format_time, read_json, merge_settings, log_action as _log_action, create_log_message, format_text, print_colored_text, reboot_current_script, noop, launch_in_new_terminal, safe_replace
from custom_modules.ege import create_text_blit, scale_position, rect_to_tuple

import_time = datetime.now() - import_time

def main(info_queues: Optional[list[Queue]] = None, commands_queue: Optional[Queue] = None) -> None:
    '''
    Main function of the snake game.
    
    :param info_queues: list of queues to send snake info to
    :type info_queues: Optional[list[Queue]]
    :param commands_queue: queue to receive commands from
    :type commands_queue: Optional[Queue]
    '''

    # Reads and initializes settings

    default_settings = {}
    for file in ['.default settings.json', '.default config.json']:
        default_settings.update(read_json(file))

    user_settings: dict = read_json('settings.json', {'name': 'Joker'})

    settings: dict = merge_settings(user_settings, default_settings)

    version = [version[1] for version in read_json('.version.json').items()]
    settings['version'] = f'{version[0]}.{version[1]}.{version[2]} B({version[3]})'

    custom_error_message = settings['custom error message']
    generate_error_report = settings['generate error report']
    overwrite_error_reports = settings['overwrite error reports']

    error_report_start_text = settings['error report text start']
    error_report_version_text = format_text(settings['error report text version'], settings['error report text version variable index'], settings['version'])
    error_report_date_text = format_text(settings['error report text date'], settings['error report text date variable index'], datetime.now())
    error_report_platform_text = format_text(settings['error report text platform'], settings['error report text platform variable index'], sys.platform)
    error_report_python_version_text = format_text(settings['error report text python version'], settings['error report text python version variable index'], sys.version)
    error_report_pygame_version_text = format_text(settings['error report text pygame version'], settings['error report text pygame version variable index'], pygame.version.ver)

    sdl_version = pygame.get_sdl_version()
    error_report_sdl_version_text = format_text(settings['error report text sdl version'], settings['error report text sdl version variable index'], f'{sdl_version[0]}.{sdl_version[1]}.{sdl_version[2]}')
    
    integrity = read_json('.integrity.json')
    integrity_cwd = set(integrity['CWD'])
    cwd = set(listdir('.'))
    error_report_integrity_text = format_text(settings['error report text integrity'], settings['error report text integrity variable index'], settings['error report text integrity successful'] if integrity_cwd.issubset(cwd) else format_text(settings['error report text integrity failed'], settings['error report text integrity failed variable index'], integrity_cwd - cwd))

    error_occurred = False
    exiting_game = threading.Event()
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        ''' Global exception handler that catches all unhandled exceptions, prints a custom error message or the default traceback, generates an error report if enabled, and sends a signal to any info queues before exiting the program. It also ignores exceptions caused by quitting the game or shutting down pygame. '''

        nonlocal error_occurred

        if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit) or exiting_game.is_set(): # Ignore any errors when shuting down pygame
            return
        
        if custom_error_message:
            print_colored_text(f'An error has occurred: Type: {exc_type} | Value: {exc_value}\nPlease report this to a developer via Discord or Github!', [255, 0, 0])
        else:
            print_exception(exc_type, exc_value, exc_traceback)


        if generate_error_report:
            if not Path('error report.txt').exists() or (not error_occurred and overwrite_error_reports):
                with open('error report.txt', 'w') as f:
                    f.write('')
            with open('error report.txt', 'a') as f:
                f.write(f'{error_report_start_text}\n{error_report_version_text}\n{error_report_date_text}\n{error_report_platform_text}\n{error_report_python_version_text}\n{error_report_pygame_version_text}\n{error_report_sdl_version_text}\n{error_report_integrity_text}\n\n')

            with open('error report.txt', 'a') as f:
                for line in format_exception(exc_type, exc_value, exc_traceback):
                    f.write(line)
            if settings['log']:
                with open('.log.log', 'r') as f:
                    log_content =  '\n' + f.read()
                with open('error report.txt', 'a') as f:
                    f.write(log_content)
            print('error report generated at: "./error report.txt"')
            if not settings['log']:
                print('Logging wasn\'t enabled, would you please enable it and re-run the program to encounter the error with logging enabled.')
            if not launch_in_new_terminal(str(Path('error handler.py').absolute())):
                print('No supported terminal emulator found. Please run "error handler.py" manually.')


        if info_queues is not None:
            for queue in info_queues:
                queue.put(-3)
                # This is necessary to send the info before the _exit kills everything
                queue.close()
                queue.join_thread()
        _exit(1)

        error_occurred = True

    def thread_excepthook(args):
        sys.excepthook(args.exc_type, args.exc_value, args.exc_traceback)

    sys.excepthook = global_exception_handler # replace the default error handler with our own.
    threading.excepthook = thread_excepthook # Also, so other threads access the same handler

    if settings['compatibility']:
        if sys.platform == 'win32':
            print_colored_text('Warning you are running on windows with compatibility mode on!\nSome setting have been automatically changed.', [255, 255, 0])
            settings['slower key inputs'] = False
            settings['busy loop threshold'] = 0.001


    if not settings['fullscreen']:
        screen_size: list[int] = settings['screen size'] # Resolution should be able to cleanly divisible by the sector size, x to x and y to y. (x, y)
    background_color: list[int] = settings['background color']
    grid_lines_color: list[int] = settings['grid lines color']
    fps: int = settings['fps']
    ups: int = settings['ups']
    if ups == 'max speed':
        ups = 887
    log: bool = settings['log']
    gui: bool = settings['GUI']

    if not gui:
        settings['skip start menu'] = True
        settings['skip end screen'] = True

    sector_size: list[int] = settings['sector size'] # Needs to be able to cleanly divisible by steps
    step: int = settings['step'] # Needs to be able to cleanly divisible by sector size, both x and y. If you change this while the script is running be sure to recalculate steps

    portals: bool = settings['portals']
    eating_speed_up: bool = settings['eating speeds you up']
    eating_speed_up_amount: int = settings['eating speed you up amount']
    snakes_count: int = settings['snakes count']

    if log:
        last_log_time = datetime.now()
        relative_log_time = settings['relative log time']

        def log_action(action: str, action_type: str):
            '''
            Logs an action with a timestamp to a specified log file.
            
            :param action: The action to log
            :type action: str
            :param action_type: The type or category of the action being logged
            :type action_type: str
            '''

            nonlocal last_log_time

            _log_action(create_log_message(action, action_type, last_log_time=last_log_time, relative_time=relative_log_time))
            last_log_time = datetime.now()

        if not Path('.log.log').exists() or settings['reset log']:
            with open('.log.log', 'w') as f:
                f.write('')
        _log_action(format_text(settings['log text for new session'], settings['log new session text time var index'], datetime.now()))
        log_action(f'import time: {import_time}', 'INFO')
        log_action('settings loaded', 'INFO')


    busy_loop_threshold = settings['busy loop threshold']

    class Advanced_clock():
        '''
        A custom clock class that allows for more accurate timing and fps/ups calculation. It uses a combination of sleep and busy waiting to achieve the desired frame time.
        
        :param fps: frames per second or updates per second to maintain
        '''

        def __init__(self, fps: int):
            self._last_frame = perf_counter()
            self._frame_time = 1 / (fps + 1)
            self.actual_frame_time = 0.00001

        def tick(self) -> None:
            '''Sleeps and busy waits until the desired frame time has passed since the last frame. It also updates the actual frame time for fps/ups calculation.'''

            remaining = self._frame_time - (perf_counter() - self._last_frame)
            if remaining > busy_loop_threshold:
                sleep(remaining - busy_loop_threshold)
            while perf_counter() - self._last_frame < self._frame_time:
                pass

            finish_time = perf_counter()
            self.actual_frame_time = finish_time - self._last_frame
            self._last_frame = finish_time
        
        def get_fps(self) -> float:
            '''Returns the current frames per second or updates per second based on the actual frame time.'''

            return 1 / self.actual_frame_time

        def update(self, fps: int) -> None:
            '''Updates the target fps/ups and recalculates the frame time.'''

            self._frame_time = 1 / (fps + 1)

    # Handles screen and other gui elements

    pygame.init()

    if gui:
        if settings['borderless']:
            flag = pygame.NOFRAME
        elif settings['resizable window']:
            flag = pygame.RESIZABLE
        else:
            flag = 0

        if settings['fullscreen']:
            screen = pygame.display.set_mode(flags=pygame.FULLSCREEN | flag)
            screen_size = screen.get_size()
        else:
            screen = pygame.display.set_mode(screen_size, flag)

        pygame.display.set_caption(settings['window name'])


        if log:
            log_action('gui initialized', 'INFO')
    

    fps_clock = Advanced_clock(fps)
    ups_clocks = [Advanced_clock(ups) for _ in range(snakes_count)]
    snakes_ups = [ups for _ in range(snakes_count)]

    # handles image asset initialization

    def snake_head_noop(var):
        pass

    image_assets = settings['use image assets']

    if image_assets:
        images = {}
        def load_image(name: str):
            images[name[:name.rfind('.')]] = pygame.image.load(Path(f'.images/{name}')).convert_alpha()

        def scale_image(image: pygame.Surface, size: Sequence[int, int] = sector_size) -> pygame.Surface:
            return pygame.transform.scale(image, size)

        for image_name in listdir(Path('.images')):
            load_image(image_name)
            image_name = image_name[:image_name.rfind('.')]
            images[image_name] = scale_image(images[image_name])
        snake_heads = {}

        def change_snake_head(move_direction: int) -> None:
            snake_heads[snake_index] = images[f'snake head {move_direction}']

        snake_head_changer = change_snake_head

        food_image = images['gold apple' if randint(0, 1) == 1 else 'red apple']

        if log:
            log_action('image assets loaded', 'INFO')
    else:
        snake_head_changer = snake_head_noop

    # generates a dictionary with all of the font objects

    font_settings_names = set()

    for setting in settings.keys():
        if setting.endswith('text'):
            font_settings_names.add(setting[:setting.find('text') - 1])

    fonts = {}
    for font_setting in font_settings_names:
        global_font_name = settings['font name']
        global_font_size = settings['font size']
        global_font_bold = settings['font bold']
        global_font_italic = settings['font italic']

        if font_setting == 'performance':
            global_font_name = 'JetBrainsMono-Regular.ttf'

        font_name = settings[f'{font_setting} text font']
        setting_font_size_value = settings[f'{font_setting} text font size']
        font_size = setting_font_size_value if type(setting_font_size_value) != str else eval(str(global_font_size) + setting_font_size_value)
        font_bold = settings[f'{font_setting} text bold']
        font_italic = settings[f'{font_setting} text italic']

        args = (font_name if font_name != None else global_font_name, font_size if font_size != None else global_font_size,
               font_bold if font_bold != None else global_font_bold, font_italic if font_italic != None else global_font_italic)
        fonts[font_setting] = (pygame.font.Font(Path('.fonts/' + args[0]), args[1]) if settings['use projects fonts'] else pygame.font.SysFont(*args))

    if log:
        log_action('fonts initialized', 'INFO')

    def load_clean_decimal(num: float | int | str) -> Decimal:
        '''
        loads a number as a Decimal object
        
        :param num: number to load
        :type num: float | int | str
        :return: Decimal object
        :rtype: Decimal
        '''

        return Decimal(str(num))

    # Handles all audio (music and sfx)

    audio: bool = settings['audio']
    music: bool = settings['music']
    sfx: bool = settings['sfx']
    if audio:
        master_volume = load_clean_decimal(settings['master volume'])
        music_volume = load_clean_decimal(settings['music volume'])
        eating_sfx_volume = load_clean_decimal(settings['eating sfx volume'])
        lose_sfx_volume = load_clean_decimal(settings['lose sfx volume'])


        pygame.mixer.init()

        if music:

            if type(settings['music name']) == str and settings['music name'] != 'random':
                settings['playlist'] = False

            multiple_songs = type(settings['music name']) == list
            if multiple_songs:
                music_files = settings['music name']
            else:
                music_files = []
                for music_directory in settings['music directories']:
                    music_files.extend(str(Path(music_directory + ('/' if not music_directory.endswith('/') else '') + music_file)) for music_file in listdir(Path(music_directory))) # address with name, must be saved

            play_last_song = False # Has to be here to be at least once defined in the outer scope

            def playlist() -> None:
                ''' handles the music playlist '''

                nonlocal play_last_song, queue_song

                music_index = 0
                played_music = []
                playlist_sleep_time = settings['playlist cycle time']
                sequential_playlist = settings['sequential playlist']
                fade_ms = settings['music fade out']

                music_notification_text_color = settings['music notification text color']
                music_notification_text_position = scale_position_(settings['music notification text position'])
                music_notification_variable_index = settings['music notification text variable index']
                music_notification_text = settings['music notification text']

                while True:
                    while pygame.mixer.music.get_busy() or pause.is_set(): # Got to be a better way to do this to only check one of them at a time
                        sleep(playlist_sleep_time)

                    if not any(alive):
                        exit()

                    if not play_last_song and not repeat_song and not queue_song:
                        music_name = music_files[music_index if sequential_playlist else randint(0, len(music_files) - 1)]
                        played_music.append(music_name)
                    
                    if repeat_song or queue_song:
                        music_index -= 1

                    queue_song = False # reset so we don't repeat anymore

                    if play_last_song:
                        if len(played_music) > 1:
                            played_music.pop()
                            music_name = played_music[-1]
                        play_last_song = False
                        music_index -= 1 if music_index == 1 else 2

                    pygame.mixer.music.load(music_name)
                    pygame.mixer.music.play(fade_ms=fade_ms)

                    music_index += 1
                    if music_index == len(music_files):
                        music_index = 0

                    create_notification(create_text_blit_(format_text(music_notification_text, music_notification_variable_index, music_name[:music_name.rfind('.')]), music_notification_text_color, music_notification_text_position, 'music notification'), 'music')

            pygame.mixer.music.set_volume(master_volume * music_volume)
            if not settings['playlist']:
                pygame.mixer.music.load((music_files[randint(0, len(music_files) - 1)] if settings['music name'] == 'random' or multiple_songs else settings['music name']))
        if sfx:
            lose_sfx_name = settings['lose sfx']
            multiple_sfx = type(lose_sfx_name) == list
            lose_sfx_files = lose_sfx_name if multiple_sfx else listdir('.sfx/lose')
            eating_sfx = pygame.mixer.Sound('.sfx/' + settings['eating sfx'])
            eating_sfx.set_volume(master_volume * eating_sfx_volume)
            lose_sfx = pygame.mixer.Sound('.sfx/lose/' + lose_sfx_files[randint(0, len(lose_sfx_files) - 1)] if lose_sfx_name == 'random' or multiple_sfx else lose_sfx_name)
            lose_sfx.set_volume(master_volume * lose_sfx_volume)

        if log:
            log_action('audio initialized', 'INFO')

    def create_text_blit_full_(text: str, color: Sequence[int], font: str, **anchor: tuple[int | float, int | float]) -> pygame.Surface:
        '''
        Wrapper for create_text_blit function.
        
        :param text: text to render
        :type text: str
        :param color: color of the text
        :type color: Sequence[int, int, int]
        :param position: position of the text on the screen
        :type position: Sequence[int, int]
        :param font: font to use
        :type font: str
        :return: rendered text surface and its rect
        :rtype: pygame.Surface
        '''

        return create_text_blit(text, color, fonts[font], **anchor)
    
    def create_text_blit_(text: str, color: Sequence[int], position: tuple[int | float, int | float], font: str):
        '''
        Wrapper for create_text_blit function with center anchor.
        
        :param text: text to render
        :type text: str
        :param color: color of the text
        :type color: Sequence[int]
        :param position: position of the text on the screen
        :type position: Sequence[int | float, int | float]
        :param font: font object to use
        :type font: str
        '''

        return create_text_blit_full_(text, color, font, center=position)
    
    def scale_position_(position: tuple[float, float]) -> list[float, float]:
        '''
        Wrapper for scale_position function.
        
        :param position: position to scale
        :type position: Sequence[float, float]
        :return: scaled position
        :rtype: list[float, float]
        '''

        return scale_position(position, screen_size)
    
    # Generates and handles some start up for colors

    def create_color_list(length: int, re_read_colors: bool = True) -> list[int]:
        '''
        creates a list of colors using main_colors cycle object
        
        :param length: length of the color list
        :type length: int
        :param re_read_colors: whether to re-read colors from the color generator
        :type re_read_colors: bool
        :return: list of colors
        :rtype: list[int]
        '''
        
        nonlocal main_colors

        if re_read_colors:
            main_colors = cycle(color_generator(read_from_disk=True))
        colors = []
        for _ in range(length):
            colors.append(next(main_colors))

        return colors
    
    if not image_assets:
        color_generator(settings['color pattern length'], True, settings['color scheme'], settings['color style'])
        main_colors = cycle(color_generator(read_from_disk=True))


        colors = []

        for _ in range(snakes_count):
            main_colors = cycle(color_generator(read_from_disk=True))
            for _ in range(settings['snake starting color'] + 1):
                snake_color = create_color_list(1, False)
            colors.append(snake_color)

        main_colors = cycle(color_generator(read_from_disk=True))
        for _ in range(settings['food starting color'] + 1):
            food_color = create_color_list(1, False)
        colors.append(food_color)

        if log:
            log_action('colors generated', 'INFO')

    # Generates snake starting positions and some other stats
    
    crashes: list[bool]
    alive: list[bool]
    moves: list[list[threading.Event]]
    start_up: threading.Event
    steps: int
    steps_ratio: float
    pause: threading.Event
    play_times: list[float]
    snakes: list[list[pygame.Rect]]
    food: pygame.Rect
    last_sector_index: int
    size: tuple[int, int]
    sectors: list[tuple[int, int]]
    illegal_positions: set[int]
    starting_position: list[int]
    game_started_time: datetime
    points_blittable: tuple[pygame.Surface, pygame.Rect]
    actions: list[list[int]] # 0 -> up, 1 -> left, 2 -> down, 3 -> right

    points = 0
    formatted_points_text = format_text(settings['points text'], settings['points text variable index'], points)
    keep_restarting = threading.Event()
    
    def generate_game_values():
        ''' Generates the initial values for the game, such as snake starting positions, food position, and other stats. This is separated into a function so it can be called again when restarting the game. '''

        nonlocal crashes, alive, moves, start_up, steps, steps_ratio, pause, play_times, snakes, food, last_sector_index, sectors, size, illegal_positions, starting_position, points, game_started_time, points_blittable, actions

        sectors = [(x, y) for x in range(0, screen_size[0],sector_size[0]) for y in range(0, screen_size[1], sector_size[1])] # all possible sections x and y top left corner of the sector positions
        last_sector_index = len(sectors) - 1
        size = (sector_size[0], sector_size[1])

        left_column = screen_size[1] // sector_size[1]
        top_row = screen_size[0] // sector_size[0]

        illegal_positions_ranges = [range(0, left_column), range(0, left_column * top_row - 1, left_column), range(left_column - 1, left_column * top_row - 1, left_column), range(left_column * (top_row - 1), top_row * left_column - 1)]
        illegal_positions = set()
        for position_range in illegal_positions_ranges:
            for position in position_range:
                illegal_positions.add(position)

        snakes = []
        starting_position = []

        if settings['sequential starting position']:
            between_positions_len = (left_column * top_row) // snakes_count
            for position in range(left_column + 1, left_column * top_row, between_positions_len):
                    while position in illegal_positions:
                        position += 1
                    starting_position.append(position)

        for i in range(snakes_count):
            if not settings['sequential starting position']:
                starting_position.append(randint(0, last_sector_index)) # Guess first
                while starting_position[i] in illegal_positions: # Then check if we need to regenerate it
                    starting_position[i] = randint(0, last_sector_index)
                illegal_positions.add(starting_position[i])

            head = pygame.Rect(*sectors[starting_position[i]], *size)
            snake = [head]
            snakes.append(snake)

        snakes_topleft_positions = set(snakes[snake_i][0].topleft for snake_i in range(snakes_count)) # just for the food check
        food = pygame.Rect(*sectors[randint(0, last_sector_index)], *size)
        while food.topleft in snakes_topleft_positions:
            food.update(*sectors[randint(0, last_sector_index)], *size)

        if log:
            log_action('snakes starting positions generated', 'INFO')

        crashes = [False for _ in range(snakes_count)]
        alive = [True for _ in range(snakes_count)]
        moves = [[threading.Event(), threading.Event(), threading.Event(), threading.Event()] for _ in range(snakes_count)]
        start_up = threading.Event()
        steps = sector_size[0] // step
        steps_ratio = snakes_ups[0] / step
        pause = threading.Event()
        play_times = []
        points = 0
        points_blittable = create_text_blit_(formatted_points_text, settings['points text color'], scale_position_(settings['points text position']), 'points')
        game_started_time = datetime.now()
        actions = [[] for _ in range(snakes_count)] # 0 -> up, 1 -> left, 2 -> down, 3 -> right

    generate_game_values()
    
    if log:
        log_action('other stats initialized', 'INFO')


    def move(direction: threading.Event, snake_index: int = 0) -> None:
        '''
        Docstring for move, still not done, **needs to improve more**!
        
        :param direction: Description
        :type direction: threading.Event
        '''

        for one_of_directions in moves[snake_index]:
            if direction == one_of_directions:
                one_of_directions.set()
            else:
                one_of_directions.clear()



    def update_all_volumes() -> None:
        ''' Updates the volume of all audio elements based on the current master volume and their individual volume settings. Possibly will change it to use a list or a dictionary. '''

        pygame.mixer.music.set_volume(music_volume * master_volume)
        lose_sfx.set_volume(lose_sfx_volume * master_volume)
        eating_sfx.set_volume(eating_sfx_volume * master_volume)

    volume_text = settings['volume notification text']
    volume_text_position = scale_position_(settings['volume notification text position'])
    volume_variable_index = settings['volume notification text variable index']
    volume_color = settings['volume notification text color']
    percentage_notification = settings['percentage volume notification']

    def volume_change_notification():
        notifications.append((create_text_blit_(format_text(volume_text, volume_variable_index, round(master_volume * 100) if percentage_notification else round(master_volume, 2)), volume_color, volume_text_position, 'volume notification'), 'volume'))

    def change_volume(increment: float) -> None:
        ''' Changes the master volume by the given increment, then updates all volumes and creates a notification.
        
        :param increment: The amount to change the master volume by, can be positive or negative
        :type increment: float
        '''

        update_master_volume(increment)
        update_all_volumes()
        volume_change_notification()

    if settings['clamp master volume']:
        bottom_range = settings['master volume range'][0]
        top_range = settings['master volume range'][1]

        def update_master_volume(increment: int) -> None:
            nonlocal master_volume

            new_master_volume = master_volume + increment
            if new_master_volume >= bottom_range and new_master_volume <= top_range:
                master_volume = new_master_volume
    else:
        def update_master_volume(increment: int) -> None:
            nonlocal master_volume

            master_volume += increment


    def get_key_code(key: str) -> int:
        '''
        gets the key code from a key name string
        
        :param key: key name
        :type key: str
        :return: key code
        :rtype: int
        '''

        return pygame.key.key_code(key)
    
    def get_k_code(modifier: str, attribute: str = '') -> int:
        '''
        gets the key code from a modifier and attribute string
        
        :param modifier: modifier name
        :type modifier: str
        :param attribute: attribute name
        :type attribute: str
        :return: key code
        :rtype: int
        '''

        return getattr(pygame, f'K{attribute}_{modifier.upper()}')
    
    volume_up_increment: Decimal = Decimal(str(settings['volume up increment']))
    volume_down_increment: Decimal = Decimal(str(settings['volume down increment']))

    quit_key = get_key_code(settings['quit game key'])
    move_up_key = get_key_code(settings['move up key'])
    move_left_key = get_key_code(settings['move left key'])
    move_down_key = get_key_code(settings['move down key'])
    move_right_key = get_key_code(settings['move right key'])
    forward_music_key = get_key_code(settings['forward music key'])
    backward_music_key = get_key_code(settings['backward music key'])
    repeat_current_song_key = get_key_code(settings['repeat current song key'])
    repeat_current_song_modifier_key = get_k_code(settings['repeat current song modifier key'], 'MOD')
    pause_key, pause_key_alternative = get_key_code(settings['pause key'][0]), get_key_code(settings['pause key'][1])
    performance_stats_key = get_key_code(settings['toggle performance stats key'])
    restart_key = get_key_code(settings['restart game key'])
    stopwatch_key = get_key_code(settings['toggle stopwatch key'])
    disable_soft_restart_key = get_key_code(settings['disable soft restart key'])
    crash_key = get_key_code(settings['crash game key'])

    repeat_song = False
    queue_song = False # Just if the user decides to cancel action

    if log:
        log_action('keys initialized', 'INFO')

    def handle_pygame_quit_event() -> None:
        '''The bare minimum to safely quit pygame, can be called from anywhere when we need to quit'''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for i in range(len(alive)):
                    alive[i] = False
                    pause.clear() # Just in case user quits when paused

    def key_input_for():
        '''
        handles key inputs using a for loop
        **Gets called each frame**!
        '''

        nonlocal paused_drawer, draw_grid, grid_drawer, draw_performance, performance_drawer, play_last_song, master_volume, repeat_song, queue_song, show_time, time_drawer

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for i in range(len(alive)):
                    alive[i] = False
                    pause.clear() # Just in case user quits when paused

            if event.type == pygame.KEYDOWN:
                if event.key == quit_key:
                    for i in range(len(alive)):
                        alive[i] = False
                        pause.clear()
                elif event.key == move_up_key:
                    if actions[0][0] != 2:
                        move(moves[0][0])
                elif event.key == move_left_key:
                    if actions[0][0] != 3:
                        move(moves[0][1])
                elif event.key == move_down_key:
                    if actions[0][0] != 0:
                        move(moves[0][2])
                elif event.key == move_right_key:
                    if actions[0][0] != 1:
                        move(moves[0][3])

            if event.type == pygame.KEYUP:
                mods = pygame.key.get_mods()

                if event.key == pause_key or event.key == pause_key_alternative:
                    if pause.is_set():
                        pause.clear()
                        paused_drawer = noop
                        pygame.mixer.music.unpause()
                    else:
                        pause.set()
                        paused_drawer = draw_paused
                        pygame.mixer.music.pause()
                elif event.key == pygame.K_g:
                    draw_grid = not draw_grid
                    grid_drawer = draw_grid_lines if draw_grid else noop
                elif event.key == performance_stats_key:
                    draw_performance = not draw_performance
                    performance_drawer = draw_performance_stats if draw_performance else noop
                    if draw_performance:
                        threading.Thread(target=create_performance_blits, daemon=True).start()
                elif event.key == forward_music_key:
                    pygame.mixer.music.stop()
                elif event.key == backward_music_key:
                    play_last_song = True
                    pygame.mixer.music.stop()
                elif event.key == repeat_current_song_key:
                    if mods & repeat_current_song_modifier_key:
                        repeat_song = not repeat_song
                    else:
                        queue_song = not queue_song
                elif event.key == restart_key:
                    reboot_current_script()
                elif event.key == stopwatch_key:
                    show_time = not show_time
                    time_drawer = draw_time if show_time else noop
                    if show_time:
                        threading.Thread(target=create_time_blit, daemon=True).start()
                elif event.key == disable_soft_restart_key:
                    keep_restarting.set()
                elif event.key == crash_key:
                    raise NotImplementedError('Game crashed, because you pressed the crash button!')

            if event.type == pygame.MOUSEWHEEL:
                if audio and music:
                    if event.y > 0:
                        change_volume(volume_up_increment)
                    else:
                        change_volume(-volume_down_increment)


    if commands_queue is not None:
        def _receiver() -> None:
            '''
            Receives commands from the commands queue and moves the snakes accordingly.
            0 -> up, 1 -> left, 2 -> down, 3 -> right, 4 -> quit, 5 -> pause
            0 and 2 are opposites, 1 and 3 are opposites.
            4 makes the snake quit the game.
            5. Pauses the game or all snakes.
            6. Disables the soft restart feature, so when the game exits it doesn't automatically restart, and instead fully exits the program.
            1 thread handles all snakes commands.
            1 command is a sequence of 2 integers, first is the snake index, second is the command.
            '''

            received_command: Sequence[int, int] = commands_queue.get()

            snake_index = received_command[0]
            command = received_command[1]

            if command == 0 and actions[snake_index][0] != 2:
                move(moves[snake_index][0], snake_index)
            elif command == 1 and actions[snake_index][0] != 3:
                move(moves[snake_index][1], snake_index)
            elif command == 2 and actions[snake_index][0] != 0:
                move(moves[snake_index][2], snake_index)
            elif command == 3 and actions[snake_index][0] != 1:
                move(moves[snake_index][3], snake_index)
            elif command == 4:
                alive[snake_index] = False
            elif command == 5:
                if pause.is_set():
                    pause.clear()
                else:
                    pause.set()
            elif command == 6:
                keep_restarting.set()

        def receiver() -> None:
            while True:
                _receiver()

        if not settings['wait for bot']:
            threading.Thread(target=receiver, daemon=True).start()
            receiver_handler = noop

            if log:
                log_action('commands receiver initialized', 'INFO')
        else:
            receiver_handler = _receiver


    last_alive = 0 # Needs to be here
    # @njit
    def movement(snake_index: int = 0) -> None:
        '''
        snakes and games logic function. Handles movement, collision detection, food eating, and more. Each snake has its own thread of this function.
        
        :param snake_index: index of the snake
        :type snake_index: int
        '''

        if snake_index == snakes_count - 1: # Last snake begins all of the snakes running
            start_up.set()

        start_up.wait()

        # should be here, because the _movement function is one iteration of a loop, that keeps getting repeated
        # All of these sectors are outside the screen

        increment = 0
        two_sectors_to_right = screen_size[0] + sector_size[0]
        two_sectors_to_down = screen_size[1] + sector_size[1]
        two_sectors_to_up = -sector_size[1]*2
        two_sectors_to_left = -sector_size[0]*2
        head: pygame.Rect = snakes[snake_index][0]
        snake = snakes[snake_index]
        ups = snakes_ups[snake_index]
        ups_clock = ups_clocks[snake_index]

        # If UPS is max speed then no need for the clock object
        if ups == 887:
            tick = noop
        else:
            def tick():
                ups_clock.tick()

        last_piece_food_color = settings['last piece becomes food color']
        cycle_food_colors = settings['cycle food colors']
        optimize_speed_up = settings['increase jumps with increasing ups']
        safe_food_spawn = settings['safe food spawn']
        faster_food_position = settings['faster food position']

        points_text = settings['points text']
        points_text_var_index = settings['points text variable index']
        points_text_color = settings['points text color']
        points_text_position = settings['points text position']

        snake_pause_cycle_time = settings['snake pause cycle time']

        if faster_food_position:
            all_possible_positions = set(sectors)

        def _movement():
            '''
            One iteration of the snake movement loop.
            1. Collision detection
            2. Movement
            3. Actions buffer refresh
            4. Out of bounds detection
            '''

            nonlocal food, points, ups, step, steps, increment, points_blittable, last_alive

            # Collision detection

            while pause.is_set():
                sleep(snake_pause_cycle_time)

            for i in range(3, len(snake)):
                if head.colliderect(snake[i]):
                    crashes[snake_index] = True
                    alive[snake_index] = False
                    last_alive = snake_index
                    if info_queue is not None:
                        info_queue.put(-2)

            if head.colliderect(food):
                if sfx and audio:
                    eating_sfx.play()

                if last_piece_food_color:
                    colors[snake_index].append(colors[-1][0])
                else:
                    colors[snake_index] = create_color_list(len(snake) + 1)

                if cycle_food_colors:
                    colors[-1] = create_color_list(1, False)

                food.update(*sectors[randint(0, last_sector_index)], *size)

                if safe_food_spawn:
                    all_snake_piece_positions = set(snake_piece.topleft for snake in snakes for snake_piece in snake)
                    if faster_food_position:
                        all_legal_positions = tuple(all_possible_positions.difference(all_snake_piece_positions))
                        food.update(*all_legal_positions[randint(0, len(all_legal_positions)) -1], *size)
                    else:
                        while food.topleft in all_snake_piece_positions:
                            food.update(*sectors[randint(0, last_sector_index)], *size)

                # All of these cords are one sector behind the last piece.

                behind_to_right = snake[-1].topleft[0] - sector_size[0]
                behind_to_down = snake[-1].topleft[1] - sector_size[1]
                behind_to_left = snake[-1].topleft[0] + sector_size[0]
                behind_to_up = snake[-1].topleft[1] + sector_size[1]
                match actions[snake_index][-1]:
                    case 0:
                        body = pygame.Rect(snake[-1].topleft[0], behind_to_up if behind_to_up != two_sectors_to_down else 0, *size)
                    case 1:
                        body = pygame.Rect(behind_to_left if behind_to_left != two_sectors_to_right else 0, snake[-1].topleft[1], *size)
                    case 2:
                        body = pygame.Rect(snake[-1].topleft[0], behind_to_down if behind_to_down != two_sectors_to_up else screen_size[1], *size)
                    case 3:
                        body = pygame.Rect(behind_to_right if behind_to_right != two_sectors_to_left else screen_size[0], snake[-1].topleft[1], *size)
                snake.append(body)
                actions[snake_index].append(actions[snake_index][-1])
                points += 1
                points_blittable = create_text_blit_(format_text(points_text, points_text_var_index, points), points_text_color, scale_position_(points_text_position), 'points')
                if eating_speed_up:
                    ups += eating_speed_up_amount
                    if optimize_speed_up:
                        if ups % steps_ratio == 0:
                            increment += 1
                            if sector_size[0] % (step + increment) == 0:
                                ups -= steps_ratio * increment
                                step += increment
                                steps = sector_size[0] // step
                                increment = 0
                    ups_clock.update(ups)

            # Movement

            for _ in range(steps):
                for i in range(len(snakes[snake_index]) - 1, -1, -1): # Change the range to use a precalculated number instead of calling the len function all the time.
                    match actions[snake_index][i]:
                        case 0:
                            snake[i].move_ip(0, -step)
                        case 1:
                            snake[i].move_ip(-step, 0)
                        case 2:
                            snake[i].move_ip(0, step)
                        case 3:
                            snake[i].move_ip(step, 0)
                tick()

            # Top up and refresh the actions buffer.

            if moves[snake_index][0].is_set():
                actions[snake_index].insert(0, 0)
                snake_head_changer(0)
            if moves[snake_index][1].is_set():
                actions[snake_index].insert(0, 1)
                snake_head_changer(1)
            if moves[snake_index][2].is_set():
                actions[snake_index].insert(0, 2)
                snake_head_changer(2)
            if moves[snake_index][3].is_set():
                actions[snake_index].insert(0, 3)
                snake_head_changer(3)
            actions[snake_index].pop()

            # out of bounds detections, the portal trick.

            for i in range(len(snake)):

                piece = snake[i]
                # Are necessary for correct calculations, saves previous state
                piece_bottomright = piece.bottomright
                piece_topleft = piece.topleft

                if piece_topleft[1] < 0:
                    if portals:
                        piece.update(piece.topleft[0], screen_size[1], *size)
                        if i == 0:
                            actions[snake_index][0] = 0
                    else:
                        crashes[snake_index] = True
                        alive[snake_index] = False
                if piece_bottomright[1] > screen_size[1]:
                    if portals:
                        piece.update(piece.topleft[0], -sector_size[1], *size)
                        if i == 0:
                            actions[snake_index][0] = 2
                    else:
                        crashes[snake_index] = True
                        alive[snake_index] = False

                if piece_topleft[0] < 0:
                    if portals:
                        piece.update(screen_size[0], piece.topleft[1], *size)
                        if i == 0:
                            actions[snake_index][0] = 1
                    else:
                        crashes[snake_index] = True
                        alive[snake_index] = False
                if piece_bottomright[0] > screen_size[0]:
                    if portals:
                        piece.update(-sector_size[0], piece.topleft[1], *size)
                        if i == 0:
                            actions[snake_index][0] = 3
                    else:
                        crashes[snake_index] = True
                        alive[snake_index] = False


        # Send the setting at the start
        if info_queues is not None:
            info_queue = info_queues[snake_index]
            info_queue.put(settings)
        else:
            info_queue = None # needed


        snakes_to_check = [range(0, snake_index), range(snake_index + 1, snakes_count)]
        sector_portion_x = sector_size[0] * settings['careful between snakes collision x portion']
        sector_portion_y = sector_size[1] * settings['careful between snakes collision y portion']

        if settings['careful between snakes collision detection']:
            careful_collision_detection = lambda: abs(piece.topleft[0] - head.topleft[0]) < sector_portion_x and abs(piece.topleft[1] - head.topleft[1]) < sector_portion_y # pyright: ignore[reportUndefinedVariable] # Maybe optimize this calculation to be faster
        else:
            careful_collision_detection = lambda: True

        if settings['collision between snakes']:
            def between_snakes_collision():
                for snake_range in snakes_to_check:
                    for snake_i in snake_range:
                        if alive[snake_i]:
                            for piece_index in range(len(snakes[snake_i])):
                                piece: pygame.Rect = snakes[snake_i][piece_index]
                                if head.colliderect(piece):
                                    if careful_collision_detection():
                                        if piece_index == 0:
                                            alive[snake_i] = False
                                            crashes[snake_i] = True
                                            info_queues[snake_i].put(-2)
                                        info_queue.put(-2)
                                        alive[snake_index] = False
                                        crashes[snake_index] = True
        else:
            between_snakes_collision = noop

        def serialize_noop(rect: pygame.rect) -> pygame.rect:
            ''' No operation serialize function, just returns the rect, used when we don't want to serialize data for the bot. '''
            return rect

        serialize = rect_to_tuple if settings['serialize data'] else serialize_noop

        if info_queue is not None:
            def bot_communication():
                ''' Communicates the snake position and food position to the bot through the info queue, also handles receiving commands from the bot through the commands queue if the wait for bot setting is on. '''

                new_snake_position = []
                for snake_piece_i in range(len(snake)):
                    new_snake_piece = snake[snake_piece_i].copy()
                    match actions[snake_index][snake_piece_i]:
                        case 0:
                            new_snake_piece.y -= sector_size[1]
                        case 1:
                            new_snake_piece.x -= sector_size[0]
                        case 2:
                            new_snake_piece.y += sector_size[1]
                        case 3:
                            new_snake_piece.x += sector_size[0]
                    new_snake_position.append(serialize(new_snake_piece))
                info_queue.put({'snake position': new_snake_position, 'food position': serialize(food)})
                receiver_handler()
        else:
            bot_communication = noop

        while alive[snake_index]:
            bot_communication()
            _movement()
            between_snakes_collision()
        
        play_times.append((snake_index, datetime.now() - game_started_time))


    def create_notification(text_blit: tuple[pygame.Surface, tuple[int, int]], notification_type: str) -> None:
        '''
        Creates a notification to be displayed on the screen.
        
        :param text_blit: blittable text to display in the notification, and its position on the screen
        :type text_blit: Sequence[pygame.Surface, Sequence[int, int]]
        :param notification_type: type of the notification, used to determine how to display it and if it should overwrite existing notifications of the same type
        :type notification_type: str
        '''

        notifications.append((text_blit, notification_type))

    notifications = []
    display_notifications = []

    def notification_manager():
        ''' Manages the notifications to be displayed on the screen, handles their timing and display. Runs in a separate thread. '''

        nonlocal notification_drawer, notifications

        TYPES_OF_NOTIFICATIONS = ['music', 'volume']
        OVERWRITE_NOTIFICATIONS = ['music', 'volume']

        def add_notification(notification: tuple[pygame.Surface, str]) -> None:
            ''' Adds a notification to the display notifications list, and sets the time it should be displayed until in the notifications times list. If the notification type is in the overwrite notifications list, it will remove any existing notification of the same type before adding the new one. '''

            if notification[1] in OVERWRITE_NOTIFICATIONS:
                if notification_types_present[notification[1]]:
                    for display_notification_i in range(len(display_notifications)):
                        if display_notifications[display_notification_i][1] == notification[1]:
                            notifications_times.pop(display_notification_i)
                            display_notifications.pop(display_notification_i)
                            break
                notification_types_present[notification[1]] = True

            notifications_times.append(datetime.now() + notification_display_times[notification[1]])
            display_notifications.append(notification)
            notifications.pop(0)

        notification_sleep_time = settings['notification cycle time']
        notification_waiting_time = settings['notification waiting cycle time']
        notification_display_time = timedelta(seconds=settings['notification display time'])

        notifications_times = []
        notification_display_times = {}
        notification_types_present = {'music': False, 'volume': False}

        for notification_type in TYPES_OF_NOTIFICATIONS:
            setting_notification_display_time = settings[f'{notification_type} notification display time']
            notification_display_times[notification_type] = notification_display_time if setting_notification_display_time is None else timedelta(seconds=setting_notification_display_time)


        while True:
            while notifications == []:
                sleep(notification_sleep_time) # afk when no notifications need to be displayed

            add_notification(notifications[0])

            notification_drawer = draw_notifications # turns on the drawer after being afk
            while display_notifications != []:
                for notification in notifications:
                    add_notification(notification)

                # Analyze which approach is better index or break

                for notification_time_i in range(len(notifications_times)):
                    notification_time = notifications_times[notification_time_i]
                    if notification_time < datetime.now():
                        if display_notifications[notification_time_i][1] in OVERWRITE_NOTIFICATIONS:
                            notification_types_present[display_notifications[notification_time_i][1]] = False
                        display_notifications.pop(notification_time_i)
                        notifications_times.pop(notification_time_i)
                        break

                sleep(notification_waiting_time)

            notification_drawer = noop # turns off the drawer, going back to being afk

    threading.Thread(target=notification_manager, daemon=True).start()

    if log:
        log_action('notification manager initialized', 'INFO')


    slow_key_cycle_time = settings['slow key input cycle time']

    increment = settings['hold key increment']
    min_var_value = settings['hold key minimal value']

    # Look into remaking this maybe, looks a little bit too nested.

    def check_for_holding(var: int, action) -> int:
        ''' checks if a key is being held down, and if it is, it performs the action after a certain amount of time, and then at a certain increment. Returns the new value of the variable that is being checked, to keep track of the time and increments. '''
        
        if audio:
            if var == 0:
                action()
            elif var > min_var_value and var % increment == 0:
                action()
        return var + 1

    def plus_key_action():
        change_volume(volume_up_increment)
    
    def minus_key_action():
        change_volume(-volume_down_increment)


    volume_up_key = get_k_code(settings['increase volume key'])
    volume_down_key = get_k_code(settings['decrease volume key'])

    def slow_key_inputs():
        ''' handles key inputs for keys that can be held down, to repeat the action after a certain amount of time, and then at a certain increment. Gets called each frame, but only does something when the keys are being held down. '''

        plus_counter = 0
        minus_counter = 0

        while any(alive):
            keys = pygame.key.get_pressed()

            if keys[volume_up_key]:
                plus_counter = check_for_holding(plus_counter, plus_key_action)
            else:
                plus_counter = 0

            if keys[volume_down_key]:
                minus_counter = check_for_holding(minus_counter, minus_key_action)
            else:
                minus_counter = 0

            sleep(slow_key_cycle_time)

    def key_inputs():
        ''' handles key/mouse = (all) inputs for the game '''
        key_input_for()

        # keys = pygame.key.get_pressed() # For when I want to add button presses that aren't toggles

    paused_blittable = create_text_blit_(settings['paused text'], settings['paused text color'], scale_position_(settings['paused text position']), 'paused')

    # For the drawing function, we can precalculate some values to optimize it a little bit, since it is called every frame and has some calculations in it.

    head_width = settings['snake head width']
    food_width = settings['food width']
    grid_lines_width = settings['grid lines width']

    def drawing():
        '''
        handles all drawing to the screen
        1. Draws snakes
        2. Draws food
        3. Draws points **the text**
        4. Updates the display
        '''

        for snake_index in range(len(snakes)):
            if alive[snake_index]:
                snake = snakes[snake_index]
                pygame.draw.rect(screen, colors[snake_index][0], snake[0], head_width)
                for body_i in range(1, len(snake)):
                    pygame.draw.rect(screen, colors[snake_index][body_i], snake[body_i])
        pygame.draw.rect(screen, colors[-1][0], food, food_width)

    def drawing_images():
        '''handles all drawing to the screen using images instead of rectangles'''

        for snake_index in range(len(snakes)):
            if alive[snake_index]:
                snake = snakes[snake_index]
                screen.blit(snake_heads[snake_index], snake[0])
                for body_i in range(1, len(snake)):
                    pygame.draw.rect(screen, colors[snake_index][body_i], snake[body_i])
        screen.blit(food_image, food)

    drawer = drawing_images if settings['use image assets'] else drawing

    def draw_grid_lines():
        for sector in sectors:
            pygame.draw.rect(screen, grid_lines_color, (*sector, sector_size[0], sector_size[1]), grid_lines_width)

    draw_grid = settings['grid lines']
    grid_drawer = draw_grid_lines if draw_grid else noop

    def draw_paused():
        screen.blit(*paused_blittable)

    paused_drawer = draw_paused if pause.is_set() else noop

    # Calculate the offset for the performance text

    fps_index = settings['performance text variable fps index']
    ups_index = settings['performance text variable ups index']

    if settings['round performance stats']:
        # Defined here, because they are used for the round function in a hot loop

        fps_precision = settings['fps round decimal places']
        ups_precision = settings['ups round decimal places']

        extra_float_spacing_fps = 1 + fps_precision
        extra_float_spacing_ups = 1 + ups_precision
    else:
        extra_float_spacing_fps = 0
        extra_float_spacing_ups = 0

    # Space character in numbers place (placeholders)
    fps_text_space = (len(str(int(fps))) + settings['extra performance text fps spacing'] + extra_float_spacing_fps) * ' '
    ups_text_space = (len(str(int(ups))) + settings['extra performance text ups spacing'] + extra_float_spacing_ups) * ' '

    # Need to format whole text in the correct order from left to right.
    # Myb change this to look cleaner!!!
    if fps_index < ups_index:
        formatted_performance_text = format_text(settings['performance text'], settings['performance text variable fps index'], fps_text_space)
        formatted_performance_text = format_text(formatted_performance_text, settings['performance text variable ups index'] + len(formatted_performance_text) - len(settings['performance text']), ups_text_space)
    else:
        formatted_performance_text = format_text(settings['performance text'], settings['performance text variable ups index'], ups_text_space)
        formatted_performance_text = format_text(formatted_performance_text, settings['performance text variable fps index'] + len(formatted_performance_text) - len(settings['performance text']), fps_text_space)
    performance_blittable = create_text_blit_full_(formatted_performance_text, settings['performance text color'], 'performance', topleft=scale_position_(settings['performance text position']))

    first_ups_clock = ups_clocks[0]
    fps_text_position = scale_position_(settings['performance text position'])
    fps_text_position[0] += fonts['performance'].size(settings['performance text'][:fps_index] + (ups_text_space if fps_index > ups_index else ''))[0] # offset text position based on the previously written text
    ups_text_position = scale_position_(settings['performance text position'])
    ups_text_position[0] += fonts['performance'].size(settings['performance text'][:ups_index] + (fps_text_space if ups_index > fps_index else ''))[0] # offset text position based on the previously written text

    good_fps = fps * settings['good fps']
    normal_fps = fps * settings['normal fps']
    good_ups = ups * settings['good ups']
    normal_ups = ups * settings['normal ups']


    performance_text_color = settings['performance text color']

    good_fps_color = settings['good fps color']
    normal_fps_color = settings['normal fps color']
    bad_fps_color = settings['bad fps color']
    good_ups_color = settings['good ups color']
    normal_ups_color = settings['normal ups color']
    bad_ups_color = settings['bad ups color']

    if settings['color performance stats']:
        def fps_color(current_fps: int):
            if current_fps > good_fps:
                return good_fps_color
            elif current_fps > normal_fps:
                return normal_fps_color
            else:
                return bad_fps_color
        def ups_color(current_ups: int):
            if current_ups > good_ups:
                return good_ups_color
            elif current_ups > normal_ups:
                return normal_ups_color
            else:
                return bad_ups_color
    else:
        def fps_color(current_fps: int):
            return performance_text_color
        def ups_color(current_ups: int):
            return performance_text_color
        
    if settings['very high ups performance stats']:
        def format_ups(ups: float) -> float:
            return ups
        def format_fps(fps: float) -> float:
            return fps
    else:
        if settings['round performance stats']:

            def format_ups(ups: float) -> int:
                return round(ups, ups_precision)
            def format_fps(fps: float) -> int:
                return round(fps, fps_precision)
        else:
            def format_ups(ups: float) -> int:
                return int(ups)
            def format_fps(fps: float) -> int:
                return int(fps)


    performance_stats_cycle_time = settings['performance stats cycle time']
    fps_blit = None
    ups_blit = None

    def _create_performance_blits():
        '''Creates the blits for the performance stats, with the current FPS and UPS.'''

        nonlocal fps_blit, ups_blit

        current_fps = format_fps(fps_clock.get_fps())
        current_ups = format_ups(first_ups_clock.get_fps())
        fps_blit = create_text_blit_full_(str(current_fps), fps_color(current_fps), 'performance', topleft=fps_text_position)
        ups_blit = create_text_blit_full_(str(current_ups), ups_color(current_ups), 'performance', topleft=ups_text_position)

    _create_performance_blits()

    def create_performance_blits():
        '''Updates the performance blittables with the current FPS and UPS. Only updates the blits, doesn't draw them to the screen.'''

        while draw_performance:
            _create_performance_blits()
            sleep(performance_stats_cycle_time)

    def draw_performance_stats():
        '''Draws the performance stats (FPS and UPS) to the screen.'''

        screen.blit(*performance_blittable)
        screen.blit(*fps_blit)
        screen.blit(*ups_blit)

    draw_performance = settings['show performance stats']
    performance_drawer = draw_performance_stats if draw_performance else noop

    if draw_performance:
        threading.Thread(target=create_performance_blits, daemon=True).start()

    if log:
        log_action('performance display initialized', 'INFO')

    def draw_notifications():
        '''Draws the notifications that need to be displayed to the screen. Only draws the notifications that the notification manager has processed. '''

        for notification in display_notifications:
            screen.blit(*notification[0])

    notification_drawer = noop

    time_text = settings['time text']
    time_text_var_index = settings['time text variable index']
    time_text_color = settings['time text color']
    show_time_format = settings['show time format']
    time_position = settings['time text position']
    show_time_cycle = settings['show time cycle time']

    show_time = settings['show time']

    time_blit = None

    def create_time_blit():
        '''Updates the time blittable with the current play time.'''

        nonlocal time_blit

        while show_time:
            time_blit = create_text_blit_(format_text(time_text, time_text_var_index, format_time((datetime.now() - game_started_time).total_seconds(), show_time_format)), time_text_color, scale_position_(time_position), 'time')
            sleep(show_time_cycle)

    def draw_time():
        screen.blit(*time_blit)
    
    if show_time:
        time_drawer = draw_time
    else:
        time_drawer = noop

    # Start menu

    if log:
        log_action('game booted up', 'INFO')


    def skip_start_menu():
        '''Skips the start menu by sending the start direction command to all snakes, and moving them in that direction once, so that the game can start.'''

        nonlocal actions

        start_direction = settings['start direction']
        for snake_index in range(snakes_count):
            actions[snake_index].append(randint(0, 3) if start_direction == 4 else start_direction)
            move(moves[snake_index][randint(0, 3) if start_direction == 4 else start_direction], snake_index)

    if settings['skip start menu']:
        skip_start_menu()
    else:
        start_menu_text = create_text_blit_(settings['start menu text'], settings['start menu text color'], scale_position_(settings['start menu text position']), 'start menu')
        version_text = create_text_blit_(format_text(settings['version text'], settings['version text variable index'], settings['version']), settings['version text color'], scale_position_(settings['version text position']), 'version')

        while actions[0] == [] and any(alive):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    for i in range(len(alive)):
                        exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == quit_key:
                        for i in range(len(alive)):
                            exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                for snake_index in range(snakes_count):
                    actions[snake_index].append(0)
                    move(moves[snake_index][0], snake_index)
                    snake_head_changer(0)
                break
            if keys[pygame.K_a]:
                for snake_index in range(snakes_count):
                    actions[snake_index].append(1)
                    move(moves[snake_index][1], snake_index)
                    snake_head_changer(1)
                break
            if keys[pygame.K_s]:
                for snake_index in range(snakes_count):
                    actions[snake_index].append(2)
                    move(moves[snake_index][2], snake_index)
                    snake_head_changer(2)
                break
            if keys[pygame.K_d]:
                for snake_index in range(snakes_count):
                    actions[snake_index].append(3)
                    move(moves[snake_index][3], snake_index)
                    snake_head_changer(3)
                break

            screen.fill(background_color)
            screen.blit(*start_menu_text)
            screen.blit(*version_text)
            pygame.display.flip()

            fps_clock.tick()

    # Needs to after we have gotten the game start time stamp
    if show_time:
        game_started_time = datetime.now()
        threading.Thread(target=create_time_blit, daemon=True).start()

    # Launching snake logic

    snake_threads = list[threading.Thread]
    key_handler: Callable[[], None]

    def launch_game_threads():
        ''' Launches all of the necessary threads for the game logic, like the snake movement threads, the playlist thread if the playlist setting is on, and the key inputs thread if the slower key inputs setting is on. '''

        nonlocal snake_threads, repeat_song, key_handler

        snake_threads = []

        for snake_index in range(snakes_count):
            snake_threads.append(threading.Thread(target=movement, daemon=True, args=[snake_index]))
            snake_threads[snake_index].start()

        if log:
            log_action('snake logic initialized', 'INFO')

        if audio and music:
            if settings['playlist']:
                threading.Thread(target=playlist, daemon=True).start()

                # Just so that the playlist can launch at least a song, before we try to repeat it.
                while not pygame.mixer.music.get_busy():
                    sleep(0.001)
                repeat_song = settings['repeat song']
            else:
                pygame.mixer.music.play(-1, fade_ms=settings['music fade out'])

            if log:
                log_action('music initialized', 'INFO')


        if settings['disable key inputs']:
            key_handler = handle_pygame_quit_event
        else:
            if settings['slower key inputs']:

                key_input_cycle_time = settings['key inputs cycle time']

                def thread_key_inputs():
                    '''Thread target for handling key inputs with a sleep in between to make them slower.'''

                    while any(alive):
                        key_inputs()
                        sleep(key_input_cycle_time)

                threading.Thread(target=thread_key_inputs, daemon=True).start()
                key_handler = noop
            else:
                key_handler = key_inputs

            if log:
                log_action('key inputs initialized', 'INFO')

            threading.Thread(target=slow_key_inputs, daemon=True).start()

            if log:
                log_action('slow key inputs initialized', 'INFO')

    launch_game_threads()

    # GUI main loop

    def gui_loop():
        ''' Main loop for handling all GUI updates and drawing. Runs until the game is left. '''

        while any(alive):
            key_handler()
            screen.fill(background_color)
            grid_drawer()
            drawer()
            screen.blit(*points_blittable)
            paused_drawer()
            performance_drawer()
            notification_drawer()
            time_drawer()

            pygame.display.flip()
            fps_clock.tick()

    gui_loop_handler = gui_loop if gui else noop
    gui_loop_handler()


    def game_left_cleanup():
        ''' Handles all of the necessary cleanup after the game has been left, like stopping the music, showing the end screen, and more. '''
        # Waits for all threads to fully leave

        for snake_thread in snake_threads:
            snake_thread.join()

        if audio:
            if music:
                pygame.mixer.music.stop()
            if all(crashes):
                if sfx:
                    lose_sfx.play()

    game_left_cleanup()

    # Save file management

    rating_points_multiplier = settings['rating points multiplier']
    rating_play_time_multiplier = settings['rating play time multiplier']
    rating_points_portion = settings['rating points portion']
    rating_play_time_portion = settings['rating play time portion']
    def rating_formula(points: int, play_time: float) -> int:
        '''
        Calculates the rating based on the points and play time, using the multipliers and portions from the settings. The result is rounded to the nearest integer. 
        :param points: the points scored by the player in the game
        :type points: int
        :param play_time: the play time of the player in the game, in seconds
        :type play_time: float
        :return: the calculated rating
        :rtype: int
        '''

        return round(points * rating_points_multiplier * rating_points_portion - play_time * rating_play_time_multiplier * rating_play_time_portion)
    
    play_time = play_times[0][1].total_seconds() # change this!
    rating = rating_formula(points, play_time)

    def save_info(default_values: dict[str: dict[str: Any]] = {settings['name']: {'high score': points, 'lowest play time': play_time, 'best rating': rating}}, user_name: str = settings['name'], save_file_name: str | Path = '.save.json', temp_file_name: str | Path = '.save_temp.json') -> dict[str: Any]:
        ''' Handles the save file management, creates a new save file if it doesn't exist, creates a new profile for the user if they haven't played before, and updates the user's save data with new stats if they are better than the previous ones.
        
        :param default_values: a dictionary containing the default save data for a user, used to create a new save file or a new profile for a user that hasn't played before
        :type default_values: dict[str: dict[str: Any]]
        :param user_name: the name of the user, used as a key in the save file to store the user's save data
        :type user_name: str
        :param save_file_name: the name of the save file, defaults to '.save.json'
        :type save_file_name: str | Path, optional
        :return: the user's save data after being updated with the new score and play time if they are better than the previous ones
        :rtype: dict[str: Any]
        '''

        nonlocal play_time, rating


        play_time = play_times[0][1].total_seconds() # change this!
        rating = rating_formula(points, play_time)

        # Create it if it doesn't exist
        if not Path(save_file_name).exists():
            with open(temp_file_name, 'w') as f:
                dump(default_values, f)
                f.flush()
                fsync(f.fileno())
            safe_replace(temp_file_name, save_file_name) # Atomic swap

            user_save = default_values[user_name]
        else:
            with open(save_file_name, 'r') as f:
                save: dict = load(f)
            user_save = save.get(user_name)

            # If current user hasn't ever played then a new profile created in the save file
            if user_save is None:
                user_save = default_values[user_name]
            else:
                if user_save['high score'] < points:
                    user_save['high score'] = points
                if user_save['lowest play time'] > play_time:
                    user_save['lowest play time'] = play_time
                if user_save['best rating'] < rating:
                    user_save['best rating'] = rating

            # Update the save file
            save[user_name] = user_save
            with open(temp_file_name, 'w') as f:
                dump(save, f)
                f.flush()
                fsync(f.fileno())
            safe_replace(temp_file_name, save_file_name) # Atomic swap

        return user_save

    user_save = save_info()

    if log:
        log_action('game ended', 'INFO')


    # Remake this to use some central function.

    TEXT_SETTING_KEYS = ['bye', 'end screen high score', 'end screen best rating', 'end screen points', 'end screen rating']
    text_sentences = [settings['lost text'] if all(crashes) else settings['quit text'], format_text(settings['end screen high score text'], settings['end screen high score text variable index'], user_save['high score'])]
    
    values = {'end screen best rating': user_save['best rating'], 'end screen points': points, 'end screen rating': rating}
    for setting in TEXT_SETTING_KEYS[len(text_sentences):]:
        text_sentences.append(format_text(settings[f'{setting} text'], settings[f'{setting} text variable index'], values[setting]))
    text_colors = [settings['lost text color'] if all(crashes) else settings['quit text color']]
    for setting in TEXT_SETTING_KEYS[len(text_colors):]:
        text_colors.append(settings[f'{setting} text color'])

    texts = []
    for i in range(len(TEXT_SETTING_KEYS)):
        texts.append(create_text_blit_(text_sentences[i], text_colors[i], scale_position_(settings[f'{TEXT_SETTING_KEYS[i]} text position']), TEXT_SETTING_KEYS[i] if i != 0 else ('lost' if all(crashes) else 'quit')))


    if settings['show last frame on end screen']:
        show_snake = settings['show last frame on end screen snake index']
        if type(show_snake) == list:
            for snake_index in show_snake:
                alive[snake_index] = True
        else:
            alive[last_alive if show_snake == -1 else show_snake] = True
        def draw_last_frame() -> None:
            ''' Draws the last frame of the game, with only the last snake alive if the setting is on. '''
            grid_drawer()
            drawer()
    else:
        draw_last_frame = noop

    ending_screen = not settings['skip end screen']

    # Need to draw it all only once, since nothing changes

    if ending_screen:
        screen.fill(background_color)
        draw_last_frame()
        for text in texts:
            screen.blit(*text)
        pygame.display.flip()

    while ending_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ending_screen = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    ending_screen = False
                elif event.key == restart_key:
                    reboot_current_script()
        fps_clock.tick()
    
    if log and not settings['skip end screen']:
        log_action('end screen ended', 'INFO')

    def send_game_stats() -> None:
        '''Sends the game stats to the bot through the info queue, if the info queue is being used.'''
        if info_queues is not None:
            for info_queue in info_queues:
                info_queue.put({'score': points, 'play time': play_time, 'rating': rating})

    game_stats_sender = noop if info_queues is None else send_game_stats

    if settings['soft restart']:
        while not keep_restarting.is_set():
            game_stats_sender()
            generate_game_values()
            skip_start_menu()
            launch_game_threads()
            gui_loop_handler()
            game_left_cleanup()
            save_info()

            
    exiting_game.set() # So that any random errors, don't appear.
    pygame.quit() # Shutdowns all pygame subprocesses
    
    # Quits all the threads. These needs to be after the pygame quits

    if not any(crashes):
        if info_queues is not None:
            for info_queue in info_queues:
                info_queue.put(-1)

    # Just in case we aren't using soft restart, when running our bot.
    game_stats_sender()

    if log:
        log_action('shutdown all pygame subprocesses', 'INFO')
        log_action('all threads ended', 'INFO')
        log_action('game closed', 'INFO')

if __name__ == '__main__':
    main()
