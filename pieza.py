import pygame
from constantes import *

class Pieza:
    RELLENO = 15
    BORDE = 2

    def __init__(self, fil, col, color):
        self.fil = fil
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = TAM_CASILLA * self.col + TAM_CASILLA // 2    
        self.y = TAM_CASILLA * self.fil + TAM_CASILLA // 2  

    def make_king(self):
        self.king = True

    def draw(self, win):
        radio = TAM_CASILLA // 2 - self.RELLENO
        pygame.draw.circle(win, GRIS, (self.x, self.y), radio + self.BORDE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radio)
        if self.king:
            win.blit(CORONA, (self.x - CORONA.get_width() // 2, self.y - CORONA.get_height() // 2))

    def move(self, fil, col):
        self.fil = fil
        self.col = col
        self.calc_pos()
    
    def __repr__(self):
        return str(self.color)
