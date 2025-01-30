import os
import sys
import pygame
import random
import time
from constantes import *
from pieza import Pieza
from tablero import Tablero
from minimax import minimax, obtener_movimientos_posibles

class Juego:
    def __init__(self, win):
        self.win = win
        self._init()
        self.start_time = time.time()
        self.profundidad_minimax = random.randint(1, 3)

    def _init(self):
        self.selected = None
        self.tablero = Tablero()
        self.turn = BLANCO
        self.movimientos_validos = {}
        self.game_over = False
        self.movimientos_sin_captura = 0
        self.movimientos_totales = 0
        self.piezas_iniciales_rojas = 2
        self.piezas_iniciales_blancas = 2

    def update(self):
        self.tablero.draw(self.win)
        self.draw_movimientos_validos(self.movimientos_validos)
        self.draw_indicators()
        pygame.display.update()

        if not self.game_over:
            self.check_ganador()

    def draw_indicators(self):
        font = pygame.font.Font(None, 20)
        turn_text = font.render(f"Turno: {'IA' if self.turn == BLANCO else 'Humano'}", True, TEXT)
        moves_text = font.render(f"Mov. Totales: {self.movimientos_totales}", True, TEXT)
        deep_text = font.render(f"Profundidad: {self.profundidad_minimax}", True, TEXT)

        if self.movimientos_sin_captura >= 1:
            moves_cap = font.render(f"Mov. sin captura: {self.movimientos_sin_captura}", True, TEXT)
            self.win.blit(moves_cap, (10, 55))
        
        self.win.blit(turn_text, (10, 10))
        self.win.blit(moves_text, (10, 25))
        self.win.blit(deep_text, (10, 40))

    def ganador(self):
        return self.tablero.ganador()

    def reset(self):
        self._init()

    def select(self, fil, col):
        if self.game_over:
            return

        if self.check_blocked(self.turn):
            self.game_over = True
            self.check_ganador()
            return

        if self.selected:
            result = self._move(fil, col)
            if result:
                self.selected = None
            else:
                self.selected = None
                self.select(fil, col)
                return

        pieza = self.tablero.get_pieza(fil, col)
        if pieza != 0 and pieza.color == self.turn:
            self.selected = pieza
            self.movimientos_validos = self.tablero.get_movimientos_validos(pieza)

            if not self.movimientos_validos:
                self.selected = None
                self.movimientos_validos = {}
            return True
        return False

    def _move(self, fil, col):
        pieza = self.tablero.get_pieza(fil, col)
        if self.selected and pieza == 0 and (fil, col) in self.movimientos_validos:
            self.tablero.move(self.selected, fil, col)
            skipped = self.movimientos_validos[(fil, col)]
            if skipped:
                for skip in skipped:
                    if self.tablero.get_pieza(skip[0], skip[1]) != 0:
                        self.tablero.eliminar([skip])
                self.movimientos_sin_captura = 0
            else:
                self.movimientos_sin_captura += 1

            if (fil == 0 and self.selected.color == ROJO) or (fil == FILAS - 1 and self.selected.color == BLANCO):
                self.selected.make_king()

            self.change_turn()
        else:
            return False
        return True

    def draw_movimientos_validos(self, movimientos):
        for move in movimientos:
            fil, col = move
            pygame.draw.circle(self.win, AZUL, 
                             (col * TAM_CASILLA + TAM_CASILLA // 2, 
                              fil * TAM_CASILLA + TAM_CASILLA // 2), 15)

    def change_turn(self):
        self.turn = BLANCO if self.turn == ROJO else ROJO
        self.movimientos_validos = {}
        self.movimientos_totales += 1

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
        message = None
        resultado = ""

        if ganador is not None:
            if ganador == BLANCO:
                message = "Has sido vencido por la IA."
                resultado = "Ganó la IA"
            elif ganador == ROJO:
                message = "¡Felicidades! Has vencido a la IA."
                resultado = "Ganó el Humano"
        elif self.check_blocked(self.turn):
            if self.turn == BLANCO:
                message = "El jugador BLANCO está bloqueado. ¡Felicidades! Has vencido a la IA."
                resultado = "Ganó el Humano por bloqueo"
            else:
                message = "El jugador ROJO está bloqueado. Has sido vencido por la IA."
                resultado = "Ganó la IA por bloqueo"
        elif self.movimientos_sin_captura >= 64:
            message = "Empate: Se alcanzaron 64 movimientos sin capturas."
            resultado = "Empate"

        if message:
            self.game_over = True
            self.show_game_over_message(message, resultado)

    def ai_move(self):
        if self.game_over:
            return
        
        self.update()
        pygame.time.wait(500)

        mejor_movimiento = None
        mejor_puntuacion = float('-inf')
        for movimiento in obtener_movimientos_posibles(self.tablero, BLANCO):
            puntuacion = minimax(movimiento, self.profundidad_minimax, False)
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_movimiento = movimiento

        if mejor_movimiento:
            self.tablero = mejor_movimiento
            self.change_turn()
            self.update()
            self.check_ganador()

    def mostrar_estadisticas(self, resultado):
        end_time = time.time()
        tiempo_total = end_time - self.start_time

        capturas_blancas = self.piezas_iniciales_rojas - self.tablero.ROJO_left
        capturas_rojas = self.piezas_iniciales_blancas - self.tablero.BLANCO_left

        print(f"Partida terminada. {resultado}")
        print(f"Movimientos totales: {self.movimientos_totales}")
        print(f"Fichas capturadas por las blancas: {capturas_blancas}")
        print(f"Fichas capturadas por las rojas: {capturas_rojas}")
        print(f"Profundidad de Minimax: {self.profundidad_minimax}")
        print(f"Tiempo total de juego: {tiempo_total:.2f} segundos")

    def show_game_over_message(self, message, resultado):
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        max_width = self.win.get_width() - 20

        lines_message = dividir_texto(message, font, max_width)
        rendered_lines_message = [font.render(line, True, (255, 255, 255)) for line in lines_message]

        total_height_message = sum(line.get_height() for line in rendered_lines_message)
        current_y_message = (self.win.get_height() - total_height_message) // 2 - 50

        background_rect_message = pygame.Rect(10, current_y_message - 35, max_width, total_height_message + 40)
        pygame.draw.rect(self.win, (120, 120, 120), background_rect_message)

        for line in rendered_lines_message:
            text_rect = line.get_rect(center=(self.win.get_width() // 2, current_y_message))
            self.win.blit(line, text_rect)
            current_y_message += line.get_height()

        pygame.display.update()
        pygame.time.wait(1000)

        end_time = time.time()
        tiempo_total = end_time - self.start_time

        capturas_blancas = self.piezas_iniciales_rojas - self.tablero.ROJO_left
        capturas_rojas = self.piezas_iniciales_blancas - self.tablero.BLANCO_left

        estadisticas = [
            f"Partida terminada. {resultado}",
            f"Movimientos totales: {self.movimientos_totales}",
            f"Fichas capturadas por las blancas: {capturas_blancas}",
            f"Fichas capturadas por las rojas: {capturas_rojas}",
            f"Profundidad de Minimax: {self.profundidad_minimax}",
            f"Tiempo total de juego: {tiempo_total:.2f} segundos"
        ]

        lines_stats = [small_font.render(stat, True, (255, 255, 255)) for stat in estadisticas]

        total_height_stats = sum(line.get_height() for line in lines_stats)
        current_y_stats = current_y_message + total_height_message + 50

        background_rect_stats = pygame.Rect(10, current_y_stats - 20, max_width, total_height_stats + 20)
        pygame.draw.rect(self.win, (128, 128, 128), background_rect_stats)

        for line in lines_stats:
            text_rect = line.get_rect(center=(self.win.get_width() // 2, current_y_stats))
            self.win.blit(line, text_rect)
            current_y_stats += line.get_height()

        pygame.display.update()
        pygame.time.wait(6500)
        pygame.quit()
        self.mostrar_estadisticas(resultado)
        exit()

def get_fil_col_from_mouse(pos):
    x, y = pos
    fil = y // TAM_CASILLA
    col = x // TAM_CASILLA
    return fil, col

def main():
    pygame.init()
    WIN = pygame.display.set_mode((ANCHO, ALTURA))
    pygame.display.set_caption('DAMAS - IA')
    
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

if __name__ == "__main__":
    main()
