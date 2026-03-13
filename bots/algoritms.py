'''This module contains various algorithms for controlling the snake in the game. Each algorithm takes the current position of the snake and the food, and returns a direction for the snake to move in. The algorithms range from simple vector-based approaches to more complex greedy strategies with randomness.
The algorithms are designed to be modular and can be easily swapped out in the main bot logic to test their performance. Each algorithm is documented with its approach and parameters for clarity.
The algorithms included in this module are:
- vector_based: A simple vector-based algorithm that calculates the direction to move based on the relative position of the food to the snake's head, prioritizing horizontal movement.
- simple_bot: A basic bot that moves towards the food without any pathfinding or collision avoidance, aligning itself first on the x-axis and then on the y-axis.
- greedy: A bot that evaluates all possible moves and chooses the one that minimizes the Manhattan distance to the food, providing smarter pathing.
- randomized: Similar to the greedy algorithm but with a chance to make a random move instead of the optimal one, adding unpredictability to the snake's behavior.
- greedy_safe_move: A bot that evaluates all possible moves and chooses the one that minimizes the Manhattan distance to the food while ensuring it doesn't collide with itself or walls, providing a safer pathing strategy.
- follow_tail: A bot that, if it cannot find a safe move towards the food, will try to follow its tail, which is always a safe move since the tail moves away.
- combined_algorithm: A bot that first tries the greedy safe move, then falls back to chasing its tail, and finally tries any safe move if all else fails, combining multiple strategies for improved performance.
- flood_fill: A helper function for the flood-fill algorithm to calculate the amount of free space available from a given position, used in the flood_safe_move algorithm.
- flood_safe_move: A bot that evaluates all possible moves and chooses the one that leads to the largest amount of free space available, using a flood-fill algorithm to calculate the score for each move, providing a more strategic approach to movement.
'''

import pygame # for documentation
from random import choice, random
from collections import deque

moves = {
0: (0, -1),  # up
1: (-1, 0),  # left
2: (0, 1),   # down
3: (1, 0)    # right
}

def vector_based(snake_pos: pygame.Rect, food_pos: pygame.Rect) -> int:
    '''A simple vector-based algorithm that calculates the direction to move based on the relative position of the food to the snake's head.
    It prioritizes horizontal movement. Algorithm created by Copilot
    
    :param snake_pos: The position of the snake's head as a pygame.Rect
    :param food_pos: The position of the food as a pygame.Rect
    :return: The direction to move (0=up, 1=left, 2=down, 3=right)
    '''
    snake_pos = snake_pos[0] # Get the head position from the list of snake segments

    dx = food_pos.x - snake_pos.x
    dy = food_pos.y - snake_pos.y

    # Prioritize horizontal movement if distance is larger horizontally
    if abs(dx) > abs(dy):
        if dx > 0:
            move_direction = 3   # right
        else:
            move_direction = 1   # left
    else:
        if dy > 0:
            move_direction = 2   # down
        else:
            move_direction = 0   # up
    return move_direction

def simple_bot(snake_pos: pygame.Rect, food_pos: pygame.Rect, move_direction: int | None = 0) -> int:
    '''A simple bot that moves towards the food without any pathfinding or collision avoidance. Algorithm created by Me
    
    :param snake_pos: The position of the snake's head as a pygame.Rect
    :param food_pos: The position of the food as a pygame.Rect
    :param move_direction: The current direction of the snake (0=up, 1=left, 2=down, 3=right)
    :return: The direction to move (0=up, 1=left, 2=down, 3=right)
    '''
    # first the bot aligns itself with the food on the x axis.
    # Then it moves up or down to get to the food.

    # The bot also checks to make sure it doesn't try to move in the opposite direction of where it's currently moving
    # It also doesn't check for collisions, so it will crash into itself if the food is behind it and it has to turn around to get to it.
    snake_pos = snake_pos[0] # Get the head position from the list of snake segments

    if snake_pos.x != food_pos.x:
        if snake_pos.x > food_pos.x:
            if move_direction == 3:
                move_direction = 2
            else:
                move_direction = 1
        else:
            if move_direction == 1:
                move_direction = 0
            else:
                move_direction = 3
    else:
        if snake_pos.y > food_pos.y:
            move_direction = 0
        else:
            move_direction = 2
    return move_direction

def greedy(snake_pos: pygame.Rect, food_pos: pygame.Rect, move_direction: int | None = 0) -> int:
    '''Greedy Manhattan Distance (Smarter Pathing) - A bot that evaluates all possible moves and chooses the one that minimizes the Manhattan distance to the food. Algorithm created by Copilot
    
    :param snake_pos: The position of the snake's head as a pygame.Rect
    :param food_pos: The position of the food as a pygame.Rect
    :param move_direction: The current direction of the snake (0=up, 1=left, 2=down, 3=right)
    :return: The direction to move (0=up, 1=left, 2=down, 3=right)
    '''
    snake_pos = snake_pos[0] # Get the head position from the list of snake segments

    best_dir = move_direction
    best_dist = abs(snake_pos.x - food_pos.x) + abs(snake_pos.y - food_pos.y)

    for direction, (mx, my) in moves.items():
        new_x = snake_pos.x + mx
        new_y = snake_pos.y + my
        dist = abs(new_x - food_pos.x) + abs(new_y - food_pos.y)

        if dist < best_dist:
            best_dist = dist
            best_dir = direction

    return best_dir

def randomized(snake_pos: pygame.Rect, food_pos: pygame.Rect) -> int:
    '''Randomized Greedy - Similar to the greedy algorithm but with a chance to make a random move instead of the optimal one, adding unpredictability. Algorithm created by Copilot
    
    :param snake_pos: The position of the snake's head as a pygame.Rect
    :param food_pos: The position of the food as a pygame.Rect
    :return: The direction to move (0=up, 1=left, 2=down, 3=right)
    '''
    snake_pos = snake_pos[0] # Get the head position from the list of snake segments
    

    options = []

    if food_pos.x > snake_pos.x:
        options.append(3)  # right
    elif food_pos.x < snake_pos.x:
        options.append(1)  # left

    if food_pos.y > snake_pos.y:
        options.append(2)  # down
    elif food_pos.y < snake_pos.y:
        options.append(0)  # up

    # Add some randomness
    if random() < 0.2:
        options.append(choice([0,1,2,3]))

    if options == []:
        options.append(0)

    return choice(options)

def is_safe(pos: pygame.Rect, snake: list[pygame.Rect], grid_w: int, grid_h: int) -> bool:
    '''Helper function to check if a position is safe for the snake to move to (not colliding with itself or walls). Algorithm created by Copilot
    
    :param pos: The head position to check as a tuple (x, y)
    :param snake: The current position of the snake as a list of pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: True if the position is safe, False otherwise
    '''

    x, y = pos
    if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
        return False
    if pos in snake[:-1]:  # allow tail since it moves
        return False
    return True

def greedy_safe_move(snake: list[pygame.Rect], food: pygame.Rect, grid_w: int | None = 640, grid_h: int | None = 480) -> int:
    '''Greedy with Safety Checks - A bot that evaluates all possible moves and chooses the one that minimizes the Manhattan distance to the food while ensuring it doesn't collide with itself or walls. Algorithm created by Copilot
    
    :param snake: The current position of the snake as a list of pygame.Rect
    :param food: The position of the food as a pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: The direction to move (0=up, 1=left, 2=down, 3=right) or None if no safe move is available
    '''

    head = snake[0]
    best_dir = None
    best_dist = 999999

    for d, (dx, dy) in moves.items():
        new_pos = (head[0] + dx, head[1] + dy)
        if not is_safe(new_pos, snake, grid_w, grid_h):
            continue

        dist = abs(new_pos[0] - food[0]) + abs(new_pos[1] - food[1])
        if dist < best_dist:
            best_dist = dist
            best_dir = d

    return best_dir

def follow_tail(snake: list[pygame.Rect], grid_w: int | None = 640, grid_h: int | None = 480) -> int:
    '''Tail Chasing (Fallback Strategy) - A bot that, if it cannot find a safe move towards the food, it will try to follow its tail, which is always a safe move since the tail moves away. Algorithm created by Copilot
    
    :param snake: The current position of the snake as a list of pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: The direction to move (0=up, 1=left, 2=down, 3=right) or None if no safe move is available
    '''

    tail = snake[-1]
    return greedy_safe_move(snake, tail, grid_w, grid_h)

def combined_algorithm(snake: list[pygame.Rect], food: pygame.Rect, grid_w: int | None = 640, grid_h: int | None = 480) -> int:
    '''Combined Algorithm - A bot that first tries the greedy safe move, then falls back to chasing its tail, and finally tries any safe move if all else fails. Algorithm created by Copilot
    
    :param snake: The current position of the snake as a list of pygame.Rect
    :param food: The position of the food as a pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: The direction to move (0=up, 1=left, 2=down, 3=right) or None if no safe move is available
    '''

    move = greedy_safe_move(snake, food, grid_w, grid_h)

    if move is None:
        # fallback: chase tail
        move = follow_tail(snake, grid_w, grid_h)

    if move is None:
        # final fallback: any safe move
        for d, (dx, dy) in moves.items():
            new_pos = (snake[0][0] + dx, snake[0][1] + dy)
            if is_safe(new_pos, snake, grid_w, grid_h):
                move = d
                break

    return move

def flood_fill(start: tuple[int, int], snake: list[pygame.Rect], grid_w: int | None = 640, grid_h: int | None = 480) -> int:
    '''Helper function for flood-fill algorithm to calculate the amount of free space available from a given position. Algorithm created by Copilot
    
    :param start: The starting position as a tuple (x, y)
    :param snake: The current position of the snake as a list of pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: The number of free cells reachable from the starting position
    '''

    visited = set()
    q = deque([start])
    body = set(snake[:-1])

    while q:
        x, y = q.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in moves.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in body:
                q.append((nx, ny))

    return len(visited)

def flood_safe_move(snake: pygame.Rect, food: pygame.Rect, grid_w: int | None = 640, grid_h: int | None = 480) -> int:
    '''Flood-Fill Based Move - A bot that evaluates all possible moves and chooses the one that leads to the largest amount of free space available, using a flood-fill algorithm to calculate the score for each move. Algorithm created by Copilot
    
    :param snake: The current position of the snake as a list of pygame.Rect
    :param food: The position of the food as a pygame.Rect
    :param grid_w: The width of the grid
    :param grid_h: The height of the grid
    :return: The direction to move (0=up, 1=left, 2=down, 3=right) or None if no safe move is available
    '''

    head = snake[0]

    best_dir = None
    best_score = -1

    for d, (dx, dy) in moves.items():
        new_pos = (head[0] + dx, head[1] + dy)
        if not is_safe(new_pos, snake, grid_w, grid_h):
            continue

        # simulate move
        new_snake = [new_pos] + snake[:-1]

        # flood-fill score = free space
        score = flood_fill(new_pos, new_snake, grid_w, grid_h)

        if score > best_score:
            best_score = score
            best_dir = d

    return best_dir


if __name__ == '__main__':
    print('This module contains algorithms for controlling the snake in the game. It is not meant to be run directly.')