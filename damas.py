import pygame
import random
from copy import deepcopy


pygame.init()
# Constantes
ANCHO, ALTURA = 600, 600
FILAS, COLUMNAS = 4, 4 
TAM_CASILLA = ANCHO // COLUMNAS

# Colores 
ROJO = (255, 105, 97)
ROJO_TAB = (255, 0, 0)
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
GRIS = (128, 128, 128)
AZUL = (59, 131, 189)
TEXT = (0,0,0)

CORONA = pygame.transform.scale(pygame.image.load("corona.png"), (45, 25))

def color_to_name(color):
        if color == ROJO:
            return 'ROJO'
        elif color == BLANCO:
            return 'BLANCO'
        return 'Desconocido'

import pygame

def dividir_texto(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word, True, (255, 0, 0))
        word_width = word_surface.get_width()
        if current_width + word_width > max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + font.render(' ', True, (255, 0, 0)).get_width()
    
    if current_line:
        lines.append(' '.join(current_line))

    return lines
   

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
            fil, col = pieza
            if self.tablero[fil][col] != 0:
                if self.tablero[fil][col].color == ROJO:
                    self.ROJO_left -= 1
                elif self.tablero[fil][col].color == BLANCO:
                    self.BLANCO_left -= 1
                self.tablero[fil][col] = 0  # Eliminar la pieza del tablero



    def ganador(self):
        if self.ROJO_left <= 0:
            return 'BLANCO'
        elif self.BLANCO_left <= 0:
            return 'ROJO'
        return None

    def get_movimientos_validos(self, pieza):
        movimientos = {}
        direcciones = []

        if pieza.king:
            direcciones = [
                (-1, -1), (-1, 1), # Movimientos diagonales hacia arriba
                (1, -1), (1, 1)    # Movimientos diagonales hacia abajo
            ]
        else:
            if pieza.color == ROJO:
                direcciones = [(-1, -1), (-1, 1)]  # Movimientos diagonales hacia arriba
            else:  # BLANCO
                direcciones = [(1, -1), (1, 1)]   # Movimientos diagonales hacia abajo

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
                    movimientos[(f, izq)] = last + skipped
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
                    movimientos[(f, der)] = last + skipped
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

class Juego:
    def __init__(self, win):
        self.win = win
        self._init()

    def _init(self):
        self.selected = None
        self.tablero = Tablero()
        self.turn = BLANCO
        self.movimientos_validos = {}
        self.game_over = False  # Variable para controlar si el juego ha terminado
        self.movimientos_sin_captura = 0 # Contador de movimientos sin capturas

    def update(self):
        self.tablero.draw(self.win)
        self.draw_movimientos_validos(self.movimientos_validos)
        pygame.display.update()

        if not self.game_over:
            self.check_ganador()

    def ganador(self):
        return self.tablero.ganador()

    def reset(self):
        self._init()

    def select(self, fil, col):
        if self.game_over:
            return

        if self.check_blocked(self.turn):
            
            if self.turn == BLANCO:
                jugador = 'BLANCO'
            elif self.turn == ROJO:
                jugador = 'ROJO'
            print(f"El jugador {jugador} está bloqueado. El juego ha terminado.")
            self.game_over = True
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
                self.game_over = True
                self.check_ganador()
            return True
        return False
    
    def _move(self, fil, col):
        pieza = self.tablero.get_pieza(fil, col)

        if self.selected and pieza == 0 and (fil, col) in self.movimientos_validos:
            print(f"Pieza movida: {self.selected.color} desde ({self.selected.fil}, {self.selected.col}) a ({fil, col})")
            self.tablero.move(self.selected, fil, col)
            skipped = self.movimientos_validos[(fil, col)]
            if skipped:
                for skip in skipped:
                    if self.tablero.get_pieza(skip[0], skip[1]).color != self.selected.color:
                        self.tablero.eliminar([skip])  # Pasar como lista de una tupla
                self.movimientos_sin_captura = 0  # Restablecer el contador al capturar una pieza
            else:
                self.movimientos_sin_captura += 1  # Incrementar el contador si no hay captura

            # Convertir en dama si llega al otro extremo del tablero
            if fil == 0 and self.selected.color == ROJO or fil == FILAS - 1 and self.selected.color == BLANCO:
                self.selected.make_king()  # Utilizar el método make_king

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
    
    def opposite_turn(self, turn):
        return ROJO if turn == BLANCO else BLANCO   

    def check_ganador(self):
        ganador = self.tablero.ganador()
        if ganador:
            message = f"El ganador es el jugador {ganador}"
            self.game_over = True
            self.show_game_over_message(message)
        elif self.check_blocked(self.turn):
            message = f"El jugador {color_to_name(self.turn)} está bloqueado. El jugador {color_to_name(self.opposite_turn(self.turn))} gana."
            self.game_over = True
            self.show_game_over_message(message)
        elif self.movimientos_sin_captura >= 64:
            message = "Empate: Se alcanzaron 64 movimientos sin capturas."
            self.game_over = True
            self.show_game_over_message(message)


    def ai_move(self):
        if self.game_over:
            return

        best_move = None
        best_score = -float('inf')

        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero.get_pieza(fil, col)
                if pieza != 0 and pieza.color == BLANCO:
                    movimientos = self.tablero.get_movimientos_validos(pieza)
                    if movimientos:
                        for move, skipped in movimientos.items():
                            new_tablero = deepcopy(self.tablero)
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

            # Actualiza la pantalla para mostrar el último movimiento
            self.update()

            # Verificar si el juego ha terminado después de actualizar la pantalla
            self.check_ganador()


    def evaluate_board(self, tablero):
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

    def show_game_over_message(self, message):
        font = pygame.font.Font(None, 36)
        max_width = self.win.get_width() - 20  # Espacio máximo permitido para el texto

        lines = dividir_texto(message, font, max_width)
        rendered_lines = [font.render(line, True, (0, 0, 0)) for line in lines]

        # Calcula la altura total del texto
        total_height = sum(line.get_height() for line in rendered_lines)
        current_y = (self.win.get_height() - total_height) // 2  # Empieza desde el centro vertical

        # Dibujar el rectángulo de fondo
        background_rect = pygame.Rect(10, current_y - 30, max_width, total_height + 35)
        pygame.draw.rect(self.win, GRIS, background_rect)  # Fondo blanco

        # Renderizar cada línea y centrarla horizontalmente
        for line in rendered_lines:
            text_rect = line.get_rect(center=(self.win.get_width() // 2, current_y))
            self.win.blit(line, text_rect)
            current_y += line.get_height()  # Avanza a la siguiente línea

        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        exit()

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
