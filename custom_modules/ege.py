'''ege -> Emilio's game engine
'''
from typing import Sequence
import pygame

def scale_position(position: Sequence[float], screen_size: Sequence[int]) -> list[float, float]:
    '''
    scales a position from relative (0.0 to 1.0) to absolute (pixels)
    
    :param position: position to scale
    :type position: Sequence[float]
    :param screen_size: size of the screen
    :type screen_size: Sequence[int]
    :return: scaled position
    :rtype: list[float, float]
    '''
    return [screen_size[0] * position[0], screen_size[1] * position[1]]

def create_text_blit(text: str, text_color: list[int, int, int], font: pygame.font, **anchor: tuple[int | float, int | float]) -> tuple[pygame.Surface, pygame.Rect]:
   '''
    creates a text blit tuple for rendering on the screen

   :param text: text to render 
   :type text: str
   :param text_color: color of the text
   :type text_color: list[int, int, int]
   :param font: font to render the text with
   :type font: pygame.font
   :param position: position to render the text at
   :type position: Sequence[int, int]
   :return: text blit tuple
   :rtype: tuple[pygame.Surface, pygame.Rect]
   '''
   text_render = font.render(text, True, text_color)
   return (text_render, text_render.get_rect(**anchor))

def rect_to_tuple(rect: pygame.rect) -> tuple[int, int, int, int]:
    '''
    converts a pygame rect to a tuple
    
    :param rect: rect to convert
    :type rect: pygame.rect
    :return: tuple representation of the rect
    :rtype: tuple[int, int, int, int]
    '''
    return (rect.x, rect.y, rect.w, rect.h)

def tuple_to_rect(serialized_data: tuple) -> pygame.Rect:
    '''
    converts a tuple of (x, y, width, height) to a pygame.Rect object. This is used because when using processes, the data is serialized and sent as tuples instead of rects.

    :param serialized_data: The serialized data of a rect, in the form of a tuple (x, y, width, height)
    :type serialized_data: tuple
    :return: The deserialized rect
    :rtype: Rect
    '''
    return pygame.Rect(serialized_data[0], serialized_data[1], serialized_data[2], serialized_data[3])