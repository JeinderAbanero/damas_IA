import pygame
from constantes import *
from pieza import Pieza

class Tablero:
    def __init__(self):
        self.tablero = []
        self.ROJO_left = self.BLANCO_left = 2
        self.ROJO_kings = self.BLANCO_kings = 0
        self.crear_tablero()

    def draw_cuadrados(self, win):
        win.fill(NEGRO)
        for fil in range(FILAS):
            for col in range(fil % 2, COLUMNAS, 2):
                pygame.draw.rect(win, ROJO_TAB, (fil * TAM_CASILLA, col * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA))

    def move(self, pieza, fil, col):
        self.tablero[pieza.fil][pieza.col], self.tablero[fil][col] = self.tablero[fil][col], self.tablero[pieza.fil][pieza.col]
        pieza.move(fil, col)
        if (fil == FILAS - 1 or fil == 0) and not pieza.king:
            pieza.make_king()
            if pieza.color == BLANCO:
                self.BLANCO_kings += 1
            else:
                self.ROJO_kings += 1

    def get_pieza(self, fil, col):
        return self.tablero[fil][col]

    def crear_tablero(self):
        for fil in range(FILAS):
            self.tablero.append([])
            for col in range(COLUMNAS):
                if col % 2 == ((fil + 1) % 2):
                    if fil < 1:
                        self.tablero[fil].append(Pieza(fil, col, BLANCO))
                    elif fil > 2:
                        self.tablero[fil].append(Pieza(fil, col, ROJO))
                    else:
                        self.tablero[fil].append(0)
                else:
                    self.tablero[fil].append(0)

    def draw(self, win):
        self.draw_cuadrados(win)
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero[fil][col]
                if pieza != 0:
                    pieza.draw(win)

    def eliminar(self, piezas):
        for pieza in piezas:
            fil, col = pieza
            if self.tablero[fil][col] != 0:
                color = self.tablero[fil][col].color
                if color == ROJO:
                    self.ROJO_left -= 1
                elif color == BLANCO:
                    self.BLANCO_left -= 1
                self.tablero[fil][col] = 0

    def ganador(self):
        if self.ROJO_left <= 0:
            return BLANCO
        elif self.BLANCO_left <= 0:
            return ROJO
        return None
    
    def get_movimientos_validos(self, pieza):
        movimientos = {}
        direcciones = []

        if pieza.king:
            direcciones = [
                (-1, -1), (-1, 1),  # Movimientos diagonales hacia arriba
                (1, -1), (1, 1)     # Movimientos diagonales hacia abajo
            ]
        else:
            if pieza.color == ROJO:
                direcciones = [(-1, -1), (-1, 1)]  # Movimientos diagonales hacia arriba
            else:  # BLANCO
                direcciones = [(1, -1), (1, 1)]    # Movimientos diagonales hacia abajo

        for dir in direcciones:
            fil, col = pieza.fil + dir[0], pieza.col + dir[1]
            if 0 <= fil < FILAS and 0 <= col < COLUMNAS:
                siguiente_fila, siguiente_columna = fil + dir[0], col + dir[1]
                if self.tablero[fil][col] == 0:  # Posición vacía
                    movimientos[(fil, col)] = []
                elif self.tablero[fil][col].color != pieza.color:
                    # Verificar que la pieza a capturar es del color opuesto
                    if 0 <= siguiente_fila < FILAS and 0 <= siguiente_columna < COLUMNAS:
                        if self.tablero[siguiente_fila][siguiente_columna] == 0:
                            movimientos[(siguiente_fila, siguiente_columna)] = [(fil, col)]

        return movimientos

    def is_blocked(self, color):
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero[fil][col]
                if pieza != 0 and pieza.color == color:
                    if self.get_movimientos_validos(pieza):
                        return False
        return True
