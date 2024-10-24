from settings import *
from tools import *
import pygame as pg


class Line:
    def __init__(self, pos1:tuple, pos2:tuple) -> None:
        self.pos1 = pos1
        self.pos2 = pos2
        
    def draw(self, screen:pg.Surface):
        pg.draw.line(screen, RED, self.pos1, self.pos2, 3)


class Button(pg.sprite.Sprite):
    def __init__(self, group:pg.sprite.Group, pos:tuple, size:tuple, text:str, color:tuple, bg_color:tuple, text_size:int, action, need_param:bool=False) -> None:
        super().__init__(group)
        self.image = pg.surface.Surface(size)
        self.image.fill(bg_color)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        text_surf = render_text(text, color, bg_color, text_size)
        text_surf:pg.Surface
        rect = text_surf.get_rect()
        rect.center = (size[0]/2, size[1]/2)
        self.image.blit(text_surf, rect)
        self.action = action
        self.need_param = need_param
        
    def draw(self, screen:pg.Surface) -> None:
        screen.blit(self.image, self.rect)

    def update(self, mouse:bool, menu:list, param=None):
        if mouse:
            x, y = pg.mouse.get_pos()
            if self.rect.collidepoint(x, y):
                if self.need_param:
                    self.action(param)
                else:
                    self.action()
                menu[0] = 0


class Text_Zone:
    def __init__(self, pos:tuple, size:tuple, text_size:int, text_color:tuple, bg_color:tuple, offset:tuple) -> None:
        self.image = pg.surface.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.text_size = text_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.offset = offset

    def draw(self, screen:pg.Surface, querry:str) -> None:
        if querry == '':
            querry = 'ENTER TEXT'
            color = LIGHT_GREY
        else:
            color = self.text_color
        text = render_text(querry, color, self.bg_color, self.text_size)
        self.image.fill(self.bg_color)
        self.image.blit(text, self.offset)
        screen.blit(self.image, self.rect)