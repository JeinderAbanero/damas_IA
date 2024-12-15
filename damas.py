import pygame
import random
from copy import deepcopy

# Constantes
ANCHO, ALTURA = 600, 600
FILAS, COLUMNAS = 4, 4 
TAM_CASILLA = ANCHO // COLUMNAS

# Colores 
ROJO = (255, 105, 97)
BLANCO = (224, 176, 255)
NEGRO = (20, 20, 20)
GRIS = (128, 128, 128)
AZUL = (59, 131, 189)

CORONA = pygame.transform.scale(pygame.image.load("corona.png"), (45, 25))

# Clases Piezas, Tablero, Juego

class Piezas: 
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


class Tablero:
    def __init__(self):
        self.tablero = []
        self.ROJO_left = self.BLANCO_left = 2
        self.ROJO_kings = self.BLANCO_kings = 0
        self.crear_tablero()

    def draw_cuadrados(self, win):  # ORDEN: rojo, blanco, rojo, blanco, rojo...
        win.fill(NEGRO)
        for fil in range(FILAS):
            for col in range(fil % 2, COLUMNAS, 2):
                pygame.draw.rect(win, ROJO, (fil * TAM_CASILLA, col * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA))

    def move(self, pieza, fil, col):
        print(f"Antes del movimiento: pieza en ({pieza.fil}, {pieza.col}), moviéndose a ({fil}, {col})")
        print(f"Estado antes de mover: ROJO_kings={self.ROJO_kings}, BLANCO_kings={self.BLANCO_kings}")

        # Intercambio de posiciones
        self.tablero[pieza.fil][pieza.col], self.tablero[fil][col] = self.tablero[fil][col], self.tablero[pieza.fil][pieza.col]
        
        # Actualizamos la posición de la pieza
        pieza.move(fil, col)

        print(f"Después del movimiento: pieza en ({pieza.fil}, {pieza.col}), moviéndose a ({fil}, {col})")
        print(f"Estado después de mover: ROJO_kings={self.ROJO_kings}, BLANCO_kings={self.BLANCO_kings}")
        
        # Verificación para convertir en reina
        if (fil == FILAS - 1 or fil == 0) and not pieza.king:  # Asegurarse de que no sea ya reina
            print(f"Pieza ({pieza.fil}, {pieza.col}) alcanzó la última fila y se convierte en reina")
            pieza.make_king()  # Convertir a reina

            if pieza.color == BLANCO: 
                self.BLANCO_kings += 1
                print(f"Pieza blanca convertida a reina: BLANCO_kings={self.BLANCO_kings}")
            else:
                self.ROJO_kings += 1
                print(f"Pieza roja convertida a reina: ROJO_kings={self.ROJO_kings}")

    def get_pieza(self, fil, col):
        return self.tablero[fil][col]

    def crear_tablero(self): 
        for fil in range(FILAS):
            self.tablero.append([]) 
            for col in range(COLUMNAS):
                if col % 2 == ((fil + 1) % 2):
                    if fil < 1:
                        self.tablero[fil].append(Piezas(fil, col, BLANCO))
                    elif fil > 2:
                        self.tablero[fil].append(Piezas(fil, col, ROJO))
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
            self.tablero[pieza.fil][pieza.col] = 0
            if pieza != 0:
                if pieza.color == ROJO:
                    self.ROJO_left -= 1
                else:
                    self.BLANCO_left -= 1

    def ganador(self):
        if self.ROJO_left <= 0:
            return 'BLANCO'
        elif self.BLANCO_left <= 0:
            return 'ROJO'
        return None

    def get_movimientos_validos(self, pieza):
        movimientos = {}
        izq = pieza.col - 1
        der = pieza.col + 1
        fil = pieza.fil

        if pieza.color == ROJO or pieza.king:
            movimientos.update(self.atravezar_izq(fil - 1, max(fil - 3, -1), -1, pieza.color, izq))
            movimientos.update(self.atravezar_der(fil - 1, max(fil - 3, -1), -1, pieza.color, der))
        if pieza.color == BLANCO or pieza.king:
            movimientos.update(self.atravezar_izq(fil + 1, min(fil + 3, FILAS), 1, pieza.color, izq))
            movimientos.update(self.atravezar_der(fil + 1, min(fil + 3, FILAS), 1, pieza.color, der))

        if not movimientos:
            print(f"¡No hay movimientos válidos para la pieza {pieza.color} en ({pieza.fil}, {pieza.col})!")
        return movimientos

    def atravezar_izq(self, start, stop, step, color, izq, skipped=[]):
        movimientos = {}
        last = []
        for f in range(start, stop, step):
            if izq < 0:
                break
            current = self.tablero[f][izq]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    movimientos[(f, izq)] = last + skipped  # Situación de salto
                else:
                    movimientos[(f, izq)] = last
                if last:
                    if step == -1:
                        fil = max(f - 3, 0)
                    else:
                        fil = min(f + 3, FILAS)
                    movimientos.update(self.atravezar_izq(f + step, fil, step, color, izq - 1, skipped=last))
                    movimientos.update(self.atravezar_der(f + step, fil, step, color, izq + 1, skipped=last))
                break
            elif current.color != color:
                if (f + step) in range(FILAS) and (izq - 1) in range(COLUMNAS):
                    next_f = f + step
                    next_c = izq - 1
                    next_pieza = self.tablero[next_f][next_c]
                    if next_pieza == 0:
                        movimientos[(next_f, next_c)] = last + [current]
                break
            else:
                last = [current]
            izq -= 1
        return movimientos

    def atravezar_der(self, start, stop, step, color, der, skipped=[]):
        movimientos = {}
        last = []
        for f in range(start, stop, step):
            if der >= COLUMNAS:
                break
            current = self.tablero[f][der]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    movimientos[(f, der)] = last + skipped  # Situación de salto
                else:
                    movimientos[(f, der)] = last
                if last:
                    if step == -1:
                        fil = max(f - 3, 0)
                    else:
                        fil = min(f + 3, FILAS)
                    movimientos.update(self.atravezar_izq(f + step, fil, step, color, der - 1, skipped=last))
                    movimientos.update(self.atravezar_der(f + step, fil, step, color, der + 1, skipped=last))
                break
            elif current.color != color:
                if (f + step) in range(FILAS) and (der + 1) in range(COLUMNAS):
                    next_f = f + step
                    next_c = der + 1
                    next_pieza = self.tablero[next_f][next_c]
                    if next_pieza == 0:
                        movimientos[(next_f, next_c)] = last + [current]
                break
            else:
                last = [current]
            der += 1
        return movimientos

    def is_blocked(self, color):
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero[fil][col]
                if pieza != 0 and pieza.color == color:
                    if self.get_movimientos_validos(pieza):
                        return False
        return True


import copy

class Juego:
    def __init__(self, win):
        self.win = win
        self._init()

    def _init(self):
        self.selected = None
        self.tablero = Tablero()
        self.turn = BLANCO
        self.movimientos_validos = {}

    def update(self):
        self.tablero.draw(self.win)
        self.draw_movimientos_validos(self.movimientos_validos)
        pygame.display.update()

    def ganador(self):
        return self.tablero.ganador()

    def reset(self):
        self._init()

    def select(self, fil, col):
        if self.check_blocked(self.turn):
            print(f"El jugador {self.turn} está bloqueado. El juego ha terminado.")
            self.check_ganador()
            return

        if self.selected:
            result = self._move(fil, col)
            if not result:
                self.selected = None
                self.select(fil, col)

        pieza = self.tablero.get_pieza(fil, col)
        print(f"Seleccionada: {pieza} en ({fil}, {col})")
        if pieza != 0 and pieza.color == self.turn:
            self.selected = pieza
            self.movimientos_validos = self.tablero.get_movimientos_validos(pieza)
            print(f"Movimientos válidos: {self.movimientos_validos}")
            
            if not self.movimientos_validos:
                print(f"El jugador {self.turn} está bloqueado.")
                self.check_ganador()
            return True
        return False

    def _move(self, fil, col):
        pieza = self.tablero.get_pieza(fil, col)
        
        if self.selected and pieza == 0 and (fil, col) in self.movimientos_validos:
            print(f"Pieza movida: {self.selected.color} desde ({self.selected.fil}, {self.selected.col}) a ({fil}, {col})")
            self.tablero.move(self.selected, fil, col)
            skipped = self.movimientos_validos[(fil, col)]
            if skipped:
                self.tablero.eliminar(skipped)
            self.change_turn()
        else:
            return False
        return True

    def draw_movimientos_validos(self, movimientos):
        for move in movimientos:
            fil, col = move
            pygame.draw.circle(self.win, AZUL, (col * TAM_CASILLA + TAM_CASILLA // 2, fil * TAM_CASILLA + TAM_CASILLA // 2), 15)
    
    def change_turn(self):
        self.turn = BLANCO if self.turn == ROJO else ROJO
        self.movimientos_validos = {}

    def check_blocked(self, turn):
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero.get_pieza(fila, col)
                if pieza != 0 and pieza.color == turn:
                    movimientos = self.tablero.get_movimientos_validos(pieza)
                    if movimientos:
                        return False
        return True

    def check_ganador(self):
        ganador = self.tablero.ganador()
        if ganador:
            print(f"El ganador es el jugador {ganador}")
            pygame.quit()
            exit()

    def ai_move(self):
        """Función de IA que selecciona un movimiento utilizando Minimax"""
        best_move = None
        best_score = -float('inf')

        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero.get_pieza(fil, col)
                if pieza != 0 and pieza.color == BLANCO:
                    movimientos = self.tablero.get_movimientos_validos(pieza)
                    for move, skipped in movimientos.items():
                        new_tablero = copy.deepcopy(self.tablero)
                        new_pieza = new_tablero.get_pieza(pieza.fil, pieza.col)
                        new_tablero.move(new_pieza, move[0], move[1])
                        if skipped:
                            new_tablero.eliminar(skipped)
                        score = self.evaluate_board(new_tablero)
                        if score > best_score:
                            best_score = score
                            best_move = (pieza, move[0], move[1], skipped)

        if best_move:
            pieza, fil, col, skipped = best_move
            self.tablero.move(pieza, fil, col)
            if skipped:
                self.tablero.eliminar(skipped)
            self.change_turn()

    def evaluate_board(self, tablero):
        """Evalúa el tablero para la IA"""
        score = 0
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = tablero.get_pieza(fil, col)
                if pieza != 0:
                    if pieza.color == BLANCO:
                        score += 1
                    else:
                        score -= 1
        return score

# MAIN

FPS = 60 

WIN = pygame.display.set_mode((ANCHO, ALTURA))

pygame.display.set_caption('DAMAS - IA')

def get_fil_col_from_mouse(pos):
    x, y = pos
    fil = y // TAM_CASILLA
    col = x // TAM_CASILLA
    return fil, col

def main():
    run = True
    clock = pygame.time.Clock()
    game = Juego(WIN)

    while run:
        clock.tick(FPS)

        if game.ganador() != None:
            print(game.ganador())
            run = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and game.turn == ROJO:
                pos = pygame.mouse.get_pos()
                fil, col = get_fil_col_from_mouse(pos)
                game.select(fil, col)
        
        if game.turn == BLANCO:
            game.ai_move()

        game.update()

    pygame.quit()

main()
