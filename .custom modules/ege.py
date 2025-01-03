'''ege -> Emilio's game engine
'''
from typing import Sequence
import pygame

def create_text_blit(text: str, text_color: list[int, int, int], position: Sequence[float], screen_size: Sequence[int], font: pygame.font) -> tuple[pygame.Surface, pygame.Rect]: # pyright: ignore[reportUndefinedVariable]
    '''
    creates a text surface and its rect for blitting
    
    :param text: text to render
    :type text: str
    :param text_color: color of the text 
    :type text_color: list[int, int, int]
    :param position: position of the text on the screen as a fraction of screen size (0.0 to 1.0)
    :type position: Sequence[float, float]
    :param screen_size: size of the screen
    :type screen_size: Sequence[int, int]
    :param font: font to use for rendering the text
    :type font: pygame.font
    :return: tuple of text surface and its rect
    :rtype: tuple[Surface, Rect]
    '''
    text_render = font.render(text, True, text_color)
    return (text_render, text_render.get_rect(center=(screen_size[0] * position[0], screen_size[1] * position[1])))