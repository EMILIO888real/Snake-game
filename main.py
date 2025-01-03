import pygame
from threading import Thread, Event
from random import randint
from itertools import cycle
from pathlib import Path
from json import load, dump
from queue import Queue
from typing import Optional, Sequence
from sys import path
from time import sleep

path.append(str(Path('.custom modules').absolute()))

from et import color_generator, read_json, merge_settings # pyright: ignore[reportMissingImports]
from ege import create_text_blit # pyright: ignore[reportMissingImports]

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

    if not settings['fullscreen']:
        screen_size: list[int] = settings['screen size'] # Resolution should be able to cleanly divisible by the sector size, x to x and y to y. (x, y)
    background_color: list[int] = settings['background color']
    grid_lines_color: list[int] = settings['grid lines color']
    points_color: list[int] = settings['points color']
    points_text: str = settings['points text']
    fps: int = settings['fps']

    sector_size: list[int] = settings['sector size'] # Needs to be able to cleanly divisible by steps
    step: int = settings['step'] # Needs to be able to cleanly divisible by sector size, both x and y. If you change this while the script is running be sure to recalculate steps
    ups: int = settings['ups']
    snake_bot_delay: float = settings['snake bot delay']

    portals: bool = settings['portals']
    eating_speed_up: bool = settings['eating speeds you up']
    eating_speed_up_amount: int = settings['eating speed you up amount']
    snakes_count: int = settings['snakes count']

    # Handles screen and other gui elements

    pygame.init()
    if settings['fullscreen']:
        screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        screen_size = screen.get_size()
    else:
        screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption(settings['window name'])
    ups_clock = pygame.time.Clock()
    fps_clock = pygame.time.Clock()
    font = pygame.font.Font(settings['font family'], settings['font size'])

    # Handles all audio (music and sfx)

    audio: bool = settings['audio']
    sfx: bool = settings['sfx']
    if audio:

        from os import listdir # sus place

        pygame.mixer.init()

        if settings['music']:
            multiple_songs = type(settings['music name']) == list
            music_files = settings['music name'] if multiple_songs else listdir('.music')

            def playlist():
                ''' handles the music playlist '''
                music_index = 0
                while True:
                    while pygame.mixer.music.get_busy():
                        sleep(0.1)
                    if not any(alive):
                        exit()
                    pygame.mixer.music.load('.music/' + music_files[music_index if settings['sequential playlist'] else randint(0, len(music_files) - 1)])
                    pygame.mixer.music.play(fade_ms=settings['music fade out'])
                    music_index += 1
                    if music_index == len(music_files):
                        music_index = 0

            pygame.mixer.music.set_volume(settings['master volume'] * settings['music volume'])
            if not settings['playlist']:
                pygame.mixer.music.load('.music/' + (music_files[randint(0, len(music_files) - 1)] if settings['music name'] == 'random' or multiple_songs else settings['music name']))
        if sfx:
            multiple_sfx = type(settings['lose sfx']) == list
            lose_sfx_files = settings['lose sfx'] if multiple_sfx else listdir('.sfx/lose')
            eating_sfx = pygame.mixer.Sound('.sfx/' + settings['eating sfx'])
            eating_sfx.set_volume(settings['master volume'] * settings['eating sfx volume'])
            lose_sfx = pygame.mixer.Sound('.sfx/lose/' + lose_sfx_files[randint(0, len(lose_sfx_files) - 1)] if settings['lose sfx'] == 'random' or multiple_sfx else settings['lose sfx'])
            lose_sfx.set_volume(settings['master volume'] * settings['lose sfx volume'])

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
    
    def create_text_blit_(text: str, color: Sequence[int], position: Sequence[int]) -> pygame.Surface:
        '''
        Wrapper for create_text_blit function.
        
        :param text: text to render
        :type text: str
        :param color: color of the text
        :type color: Sequence[int, int, int]
        :param position: position of the text on the screen
        :type position: Sequence[int, int]
        '''
        return create_text_blit(text, color, position, screen_size, font)

    if not Path('colors.txt').exists():
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

    # Generates snake starting positions and some other stats

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

    snakes_topleft_positions = set(snakes[snake][0].topleft for snake in range(snakes_count))
    food = pygame.Rect(*sectors[randint(0, last_sector_index)], *size)
    while food.topleft in snakes_topleft_positions:
        food.update(*sectors[randint(0, last_sector_index)], *size)

    crashes = [False for _ in range(snakes_count)]
    alive = [True for _ in range(snakes_count)]
    moves = [[Event(), Event(), Event(), Event()] for _ in range(snakes_count)]
    pause = False
    pressed_pause = False
    start_up = Event()
    steps = sector_size[0] // step


    actions = [[] for _ in range(snakes_count)] # 0 -> up, 1 -> left, 2 -> down, 3 -> right

    def move(direction: Event, snake_index: int = 0) -> None:
        '''
        Docstring for move, still not done, **needs to improve more**!
        
        :param direction: Description
        :type direction: Event
        '''

        for one_of_directions in moves[snake_index]:
            if direction == one_of_directions:
                one_of_directions.set()
            else:
                one_of_directions.clear()

    def key_input_for():
        ''' handles key inputs for quitting the game '''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for i in range(len(alive)):
                    alive[i] = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    for i in range(len(alive)):
                        alive[i] = False

    start_menu_text = create_text_blit_(settings['start menu text'], settings['start menu text color'], settings['start menu text position'])

    while actions[0] == [] and any(alive):
        key_input_for()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            for snake_index in range(snakes_count):
                actions[snake_index].append(0)
                move(moves[snake_index][0], snake_index)
            break
        if keys[pygame.K_a]:
            for snake_index in range(snakes_count):
                actions[snake_index].append(1)
                move(moves[snake_index][1], snake_index)
            break
        if keys[pygame.K_s]:
            for snake_index in range(snakes_count):
                actions[snake_index].append(2)
                move(moves[snake_index][2], snake_index)
            break
        if keys[pygame.K_d]:
            for snake_index in range(snakes_count):
                actions[snake_index].append(3)
                move(moves[snake_index][3], snake_index)
            break

        screen.fill(background_color)
        screen.blit(*start_menu_text)
        pygame.display.flip()

        fps_clock.tick(fps)

    def movement(snake_index: int = 0) -> None:
        '''
        snakes and games logic function. Handles movement, collision detection, food eating, and more. Each snake has its own thread of this function.
        
        :param snake_index: index of the snake
        :type snake_index: int
        '''

        start_up.wait()

        # should be here, because the _movement function is one iteration of a loop, that keeps getting repeated
        # All of these sectors are outside the screen

        two_sectors_to_right = screen_size[0] + sector_size[0]
        two_sectors_to_down = screen_size[1] + sector_size[1]
        two_sectors_to_up = -sector_size[1]*2
        two_sectors_to_left = -sector_size[0]*2
        head: pygame.Rect = snakes[snake_index][0]
        snake = snakes[snake_index]

        def _movement():
            '''
            One iteration of the snake movement loop.
            1. Collision detection
            2. Food eating
            3. Movement
            4. Out of bounds detection
            5. Actions buffer refresh
            6. Repeat
            '''

            nonlocal food, points, ups

            # Collision detection | MOVE THIS ELSEWHERE, another thread perhaps, could try this again, but had some problems with thread synchronization.

            while pause:
                sleep(0.001)

            for i in range(3, len(snake)):
                if head.colliderect(snake[i]):
                    crashes[snake_index] = True
                    alive[snake_index] = False

            if head.colliderect(food):
                if sfx and audio:
                    eating_sfx.play()

                if settings['last piece becomes food color']:
                    colors[snake_index].append(colors[-1][0])
                else:
                    colors[snake_index] = create_color_list(len(snake) + 1)

                if settings['cycle food colors']:
                    colors[-1] = create_color_list(1, False)

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
                if eating_speed_up:
                    ups += eating_speed_up_amount

            # Movement

            for _ in range(steps):
                for i in range(len(actions[snake_index]) - 1, -1, -1):
                    match actions[snake_index][i]:
                        case 0:
                            snake[i].move_ip(0, -step)
                        case 1:
                            snake[i].move_ip(-step, 0)
                        case 2:
                            snake[i].move_ip(0, step)
                        case 3:
                            snake[i].move_ip(step, 0)
                ups_clock.tick(ups)

            # Top up and refresh the actions buffer.

            if moves[snake_index][0].is_set():
                actions[snake_index].insert(0, 0)
            if moves[snake_index][1].is_set():
                actions[snake_index].insert(0, 1)
            if moves[snake_index][2].is_set():
                actions[snake_index].insert(0, 2)
            if moves[snake_index][3].is_set():
                actions[snake_index].insert(0, 3)
            actions[snake_index].pop()

            # out of bounds detections, the portal trick.

            for i in range(len(snake)):

                piece = snake[i]
                # Are necessary for correct calculations
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


        if info_queues is not None:
            info_queue = info_queues[snake_index]
        else:
            info_queue = None

        snakes_to_check = [range(0, snake_index), range(snake_index + 1, snakes_count)]

        if info_queue is None:
            while alive[snake_index]:
                _movement()
        else:
            if settings['collision between snakes']:
                while alive[snake_index]:
                    _movement()
                    for snake_range in snakes_to_check:
                        for snake_i in snake_range:
                            if alive[snake_i]:
                                for piece_index in range(len(snakes[snake_i])):
                                    piece = snakes[snake_i][piece_index]
                                    if head.colliderect(piece):
                                        if piece_index == 0:
                                            alive[snake_i] = False
                                            crashes[snake_i] = True
                                            info_queues[snake_i].put(-2)
                                        info_queue.put(-2)
                                        alive[snake_index] = False
                                        crashes[snake_index] = True
                    info_queue.put({'snake position': snake, 'food position': food})
                    sleep(snake_bot_delay)
            else:
                while alive[snake_index]:
                    _movement()
                    info_queue.put({'snake position': snake, 'food position': food})
                    sleep(snake_bot_delay)

    if commands_queue is not None:
        def receiver():

            nonlocal pause

            '''
            Receives commands from the commands queue and moves the snakes accordingly.
            0 -> up, 1 -> left, 2 -> down, 3 -> right, 4 -> quit, 5 -> pause
            0 and 2 are opposites, 1 and 3 are opposites.
            4 makes the snake quit the game.
            5. Pauses the game or all snakes.
            1 thread handles all snakes commands.
            1 command is a sequence of 2 integers, first is the snake index, second is the command.
            '''

            while any(alive):
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
                    if pause:
                        pause = False
                    else:
                        pause = True

        Thread(target=receiver, daemon=True).start()

    for snake_index in range(snakes_count):
        Thread(target=movement, daemon=True, args=[snake_index]).start()
    else:
        start_up.set()

    if audio and settings['music']:
        if settings['playlist']:
            Thread(target=playlist, daemon=True).start()
        else:
            pygame.mixer.music.play(-1, fade_ms=settings['music fade out'])

    def key_inputs():
        ''' handles key inputs for movement and pausing the game '''

        nonlocal pressed_pause, pause

        key_input_for()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and actions[0][0] != 2:
            move(moves[0][0])
        if keys[pygame.K_a] and actions[0][0] != 3:
            move(moves[0][1])
        if keys[pygame.K_s] and actions[0][0] != 0:
            move(moves[0][2])
        if keys[pygame.K_d] and actions[0][0] != 1:
            move(moves[0][3])
        if keys[pygame.K_p]:
            if pause:
                pressed_pause = False
            else:
                pressed_pause = True
        else:
            if pressed_pause:
                pause = True
            else:
                pause = False

    points = 0
    points_display_cords = font.render(points_text.replace('POINTS', str(points)), True, points_color).get_rect(center=(screen_size[0] * settings['points text position'][0], screen_size[1] * settings['points text position'][1]))

    def drawing():
        '''
        handles all drawing to the screen
        1. Draws snakes
        2. Draws food
        3. Draws points *the text*
        4. Updates the display
        '''
        for snake_index in range(len(snakes)):
            if alive[snake_index]:
                snake = snakes[snake_index]
                pygame.draw.rect(screen, colors[snake_index][0], snake[0])
                for body_i in range(len(snake)):
                    body = snake[body_i]
                    pygame.draw.rect(screen, colors[snake_index][body_i], body)
        pygame.draw.rect(screen, colors[-1][0], food, 10)
        screen.blit(font.render(points_text.replace('POINTS', str(points)), True, points_color), points_display_cords)
        pygame.display.flip()

    if settings['grid lines']:
        while any(alive):
            key_inputs()

            screen.fill(background_color)
            for sector in sectors:
                pygame.draw.rect(screen, grid_lines_color, (*sector, sector_size[0], sector_size[1]), 1)
            drawing()
            fps_clock.tick(fps)
    else:
        while any(alive):
            key_inputs()

            screen.fill(background_color)
            drawing()
            fps_clock.tick(fps)


    if not Path('.save.json').exists():
        with open('.save.json', 'w') as f:
            dump({settings['name']: {'high score': points}}, f)
        user_save = {'high score': points}
    else:
        with open('.save.json', 'r') as f:
            save: dict = load(f)
        user_save = save.get(settings['name'])

        if user_save is None:
            user_save = {}
            user_save['high score'] = points

        if user_save['high score'] < points:
            user_save['high score'] = points

        save[settings['name']] = user_save
        with open('.save.json', 'w') as f:
            dump(save, f)

    texts = []
    text_setting_keys = ['bye text position', 'end screen points text position', 'end screen high score text position']
    text_sentences = [settings['lost text'] if all(crashes) else settings['quit text'], settings['end screen points text'].replace('POINTS', str(points)), settings['end screen high score text'].replace('HIGHSCORE', str(user_save['high score']))]
    text_colors = [settings['lost color'] if all(crashes) else settings['quit color'], settings['end screen points color'], settings['end screen high score color']]

    for i in range(len(text_setting_keys)):
        texts.append(create_text_blit_(text_sentences[i], text_colors[i], settings[text_setting_keys[i]]))

    if audio:
        if settings['music']:
            pygame.mixer.music.stop()
        if all(crashes):
            if sfx:
                lose_sfx.play()

    ending_screen = True
    while ending_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ending_screen = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ending_screen = False

        screen.fill(background_color)
        for text in texts:
            screen.blit(*text)
        pygame.display.flip()
        fps_clock.tick(fps)

    pygame.quit() # Shutdowns all pygame subprocesses

    # Quits all the threads. These needs to be after the pygame quits

    if info_queues is not None:
        for info_queue in info_queues:
            info_queue.put(-1)

if __name__ == '__main__':
    main()