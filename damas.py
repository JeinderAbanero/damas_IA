import os
import sys
import pygame
import random
import time
import copy
from constantes import *
from pieza import Pieza
from tablero import Tablero
from qlearning import QLearningAgent, calcular_recompensa

class Juego:
    def __init__(self, ventana=True):
        """Inicializa el juego"""
        self.ventana = pygame.display.set_mode((ANCHO, ALTURA)) if ventana else None
        if self.ventana:
            pygame.display.set_caption('Damas')
        self.entrenando = False  # Variable para controlar si estamos en entrenamiento
        self.modo_evaluacion = False  # Nueva variable para controlar si estamos jugando contra humano
        self._init()
        self.tablero = Tablero()
        self.turn = BLANCO
        self.movimientos_validos = {}  
        self.selected = None
        self.q_agent = QLearningAgent()
        self.last_state = None
        self.last_action = None
        self.game_over = False
        self.start_time = time.time()
        self.movimientos_totales = 0
        self.movimientos_sin_captura = 0
        self.capturas_blancas = 0
        self.capturas_rojas = 0
        self.piezas_iniciales_rojas = 2
        self.piezas_iniciales_blancas = 2
        self.recompensa_total = 0  

    def _init(self):
        """Inicializa el estado del juego"""
        self.tablero = Tablero()
        self.turn = BLANCO
        self.selected = None
        self.game_over = False
        self.q_agent = QLearningAgent()
        self.movimientos_totales = 0
        self.movimientos_sin_captura = 0
        self.capturas_blancas = 0
        self.capturas_rojas = 0
        self.recompensa_total = 0
        self.start_time = time.time()

    def update(self):
        if self.ventana:
            self.tablero.draw(self.ventana)
            self.draw_movimientos_validos(self.movimientos_validos)
            self.draw_indicators()
            pygame.display.update()

        if not self.game_over:
            self.check_ganador()

    def draw_indicators(self):
        if not self.ventana:
            return
            
        font = pygame.font.Font(None, 20)
        turn_text = font.render(f"Turno: {'Humano' if self.turn == ROJO else 'IA'}", True, TEXT)
        moves_text = font.render(f"Movimientos: {self.movimientos_totales}", True, TEXT)
        
        if self.movimientos_sin_captura >= 1:
            moves_cap = font.render(f"Mov. sin captura: {self.movimientos_sin_captura}/{MAX_MOVIMIENTOS_SIN_CAPTURA}", True, TEXT)
            self.ventana.blit(moves_cap, (10, 55))
        
        self.ventana.blit(turn_text, (10, 10))
        self.ventana.blit(moves_text, (10, 25))

    def ganador(self):
        return self.tablero.ganador()

    def reset(self, mostrar_stats=True):
        """Reinicia el juego a su estado inicial"""
        self._init()
        self.tablero = Tablero()
        self.turn = ROJO
        self.movimientos_validos = {}
        self.selected = None
        self.game_over = False
        self.start_time = time.time()
        self.movimientos_totales = 0
        self.movimientos_sin_captura = 0
        self.capturas_blancas = 0
        self.capturas_rojas = 0
        # Solo mostrar estadísticas si no estamos entrenando y se solicita mostrarlas
        if not self.entrenando and mostrar_stats:
            self.mostrar_estadisticas_consola()

    def mostrar_estadisticas_partida(self):
        """Muestra las estadísticas de la partida en la ventana"""
        if not self.ventana:
            return
            
        # Obtener estadísticas del agente
        stats = self.q_agent.obtener_estadisticas()
        
        # Configurar fuente
        font = pygame.font.Font(None, 24)
        y_pos = 10
        
        # Lista de estadísticas a mostrar
        estadisticas = [
            f"Turno: {'ROJAS' if self.turn == ROJO else 'BLANCAS'}",
            f"Movimientos: {self.movimientos_totales}",
            f"Mov. sin captura: {self.movimientos_sin_captura}/{MAX_MOVIMIENTOS_SIN_CAPTURA}",
            "",
            "Estadísticas Globales:",
            f"Partidas Jugadas: {stats['total_partidas']}",
            f"Victorias: {stats['victorias']}",
            f"Derrotas: {stats['derrotas']}",
            f"Empates: {stats['empates']}",
            f"Tasa de Victorias: {stats['tasa_victorias']:.1f}%",
            f"Mov. Promedio: {stats['movimientos_promedio']:.1f}",
            f"Tiempo Promedio: {stats['tiempo_promedio']:.1f}s"
        ]
        
        # Renderizar cada línea
        for texto in estadisticas:
            text = font.render(texto, True, TEXT)
            self.ventana.blit(text, (10, y_pos))
            y_pos += 25

    def end_game(self, tipo_final):
        """Muestra el mensaje de fin de juego"""
        if not self.ventana:
            return
            
        # Crear superficie semi-transparente negra
        overlay = pygame.Surface((ANCHO, ALTURA))
        overlay.set_alpha(128)  # 50% de transparencia
        overlay.fill((0, 0, 0))
        self.ventana.blit(overlay, (0, 0))
        
        # Mostrar mensaje principal
        mensaje = self.get_resultado_texto(tipo_final)
        font_grande = pygame.font.Font(None, 50)
        text = font_grande.render(mensaje, True, (255, 255, 255))
        text_rect = text.get_rect(center=(ANCHO//2, ALTURA//2 - 50))
        self.ventana.blit(text, text_rect)
        
        # Mostrar estadísticas
        font_pequeño = pygame.font.Font(None, 30)
        stats = [
            f"Movimientos totales: {self.movimientos_totales}",
            f"Capturas Blancas: {self.capturas_blancas}",
            f"Capturas Rojas: {self.capturas_rojas}",
            f"Tiempo de juego: {int(time.time() - self.start_time)}s"
        ]
        
        y_offset = 20
        for stat in stats:
            text = font_pequeño.render(stat, True, (200, 200, 200))
            text_rect = text.get_rect(center=(ANCHO//2, ALTURA//2 + y_offset))
            self.ventana.blit(text, text_rect)
            y_offset += 30
            
        # Botones
        font_botones = pygame.font.Font(None, 40)
        nueva_partida = font_botones.render("Nueva Partida", True, (255, 255, 255))
        salir = font_botones.render("Salir", True, (255, 255, 255))
        
        # Rectángulos para los botones
        nueva_partida_rect = nueva_partida.get_rect(center=(ANCHO//2 - 100, ALTURA//2 + 150))
        salir_rect = salir.get_rect(center=(ANCHO//2 + 100, ALTURA//2 + 150))
        
        # Dibujar fondos de botones
        pygame.draw.rect(self.ventana, (0, 128, 0), nueva_partida_rect.inflate(20, 10))
        pygame.draw.rect(self.ventana, (128, 0, 0), salir_rect.inflate(20, 10))
        
        # Dibujar texto de botones
        self.ventana.blit(nueva_partida, nueva_partida_rect)
        self.ventana.blit(salir, salir_rect)
        
        pygame.display.update()
        
        # Esperar click en los botones
        esperando = True
        while esperando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if nueva_partida_rect.inflate(20, 10).collidepoint(mouse_pos):
                        self.reset()
                        esperando = False
                    elif salir_rect.inflate(20, 10).collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def get_resultado_texto(self, tipo_final):
        """Obtiene el texto del resultado según el tipo de final"""
        if tipo_final == "victoria":
            if self.tablero.ganador() == ROJO:
                return "¡Has ganado!"
            else:
                return "¡La IA ha ganado!"
        elif tipo_final == "empate":
            return "¡El juego ha terminado en empate!"
        elif tipo_final == "bloqueo":
            if self.turn == BLANCO:
                return "¡Has ganado! (IA bloqueada)"
            else:
                return "¡La IA ha ganado! (Jugador bloqueado)"
        return ""

    def ai_move(self):
        """Realiza el movimiento de la IA"""
        if self.game_over:
            return

        # Agregar retardo solo cuando hay ventana (jugando contra humano)
        if self.ventana:
            pygame.time.wait(1000)  # Esperar 1 segundo

        # Obtener el estado actual
        current_state = self.tablero

        # Obtener todos los posibles movimientos
        movimientos_posibles = self.get_all_possible_moves(BLANCO)
        if not movimientos_posibles:
            self.registrar_fin_juego("bloqueo", "derrota")
            return

        # Seleccionar el mejor movimiento según Q-Learning
        next_board = self.q_agent.get_action(current_state, movimientos_posibles)
        
        if next_board:
            # Contar piezas antes del movimiento
            piezas_antes = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                             if current_state.get_pieza(fil, col) != 0)
            
            # Actualizar el tablero
            self.tablero = next_board
            self.movimientos_totales += 1
            
            # Contar piezas después del movimiento
            piezas_despues = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                               if self.tablero.get_pieza(fil, col) != 0)
            
            # Verificar si hubo captura
            if piezas_antes > piezas_despues:
                piezas_capturadas = piezas_antes - piezas_despues
                self.capturas_blancas += piezas_capturadas
                self.movimientos_sin_captura = 0
            else:
                self.movimientos_sin_captura += 1
            
            # Actualizar visualización si hay ventana
            if self.ventana:
                self.update()
            
            # Verificar si hay ganador después del movimiento
            ganador = self.tablero.ganador()
            if ganador:
                if ganador == BLANCO:
                    self.registrar_fin_juego("victoria", "victoria")
                else:
                    self.registrar_fin_juego("victoria", "derrota")
                return
            
            # Verificar empate por movimientos sin captura
            if self.movimientos_sin_captura >= MAX_MOVIMIENTOS_SIN_CAPTURA:
                self.registrar_fin_juego("empate", "empate")
                return
            
            self.change_turn()
        if self.ventana:
            self.update()

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
        piece = self.tablero.get_pieza(self.selected.fil, self.selected.col)
        if piece != 0 and (fil, col) in self.movimientos_validos:
            # Contar piezas antes del movimiento
            piezas_antes = sum(1 for f in range(FILAS) for c in range(COLUMNAS) 
                             if self.tablero.get_pieza(f, c) != 0)
            
            # Realizar el movimiento
            skipped = self.movimientos_validos[(fil, col)]
            self.tablero.move(piece, fil, col)
            if skipped:
                self.tablero.eliminar(skipped)
                
                # Contar piezas después del movimiento
                piezas_despues = sum(1 for f in range(FILAS) for c in range(COLUMNAS) 
                                   if self.tablero.get_pieza(f, c) != 0)
                
                # La diferencia es el número de piezas capturadas
                piezas_capturadas = piezas_antes - piezas_despues
                
                # Actualizar contador según el color que movió
                if self.turn == ROJO:
                    self.capturas_rojas += piezas_capturadas
                else:
                    self.capturas_blancas += piezas_capturadas
                
                self.movimientos_sin_captura = 0
            else:
                self.movimientos_sin_captura += 1
            
            self.movimientos_totales += 1
            self.change_turn()
            return True
        return False

    def draw_movimientos_validos(self, movimientos):
        if self.ventana:
            for move in movimientos:
                fil, col = move
                pygame.draw.circle(self.ventana, AZUL, 
                                (col * TAM_CASILLA + TAM_CASILLA // 2, 
                                fil * TAM_CASILLA + TAM_CASILLA // 2), 15)

    def change_turn(self):
        self.movimientos_validos = {}
        self.selected = None
        if self.turn == ROJO:
            self.turn = BLANCO
        else:
            self.turn = ROJO

    def get_all_possible_moves(self, color):
        """Obtiene todos los movimientos posibles para un color"""
        possible_moves = []
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero.get_pieza(fil, col)
                if pieza != 0 and pieza.color == color:
                    moves = self.tablero.get_movimientos_validos(pieza)
                    for move, skipped in moves.items():
                        new_board = self.tablero.simulate_move(pieza, move[0], move[1])
                        if new_board:
                            possible_moves.append(new_board)
        return possible_moves

    def check_blocked(self, turn):
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = self.tablero.get_pieza(fil, col)
                if pieza != 0 and pieza.color == turn:
                    movimientos = self.tablero.get_movimientos_validos(pieza)
                    if movimientos:
                        return False
        return True

    def check_ganador(self):
        """Verifica si hay un ganador y registra las estadísticas de la partida"""
        # Verificar victoria por capturas
        ganador = self.tablero.ganador()
        if ganador:
            resultado = "victoria" if ganador == BLANCO else "derrota"
            self.registrar_fin_juego("victoria", resultado)
            return True

        # Verificar empate por movimientos sin captura
        if self.movimientos_sin_captura >= MAX_MOVIMIENTOS_SIN_CAPTURA:
            self.registrar_fin_juego("empate", "empate")
            return True

        # Verificar si hay bloqueo
        if self.check_blocked(self.turn):
            resultado = "victoria" if self.turn == ROJO else "derrota"
            self.registrar_fin_juego("bloqueo", resultado)
            return True
            
        return False

    def registrar_fin_juego(self, tipo_final, resultado):
        """Registra el fin del juego y actualiza estadísticas"""
        if not self.game_over:  # Solo registrar si el juego no ha terminado
            self.game_over = True
            tiempo_partida = time.time() - self.start_time
            
            # Actualizar estadísticas del agente silenciosamente durante el entrenamiento
            if self.q_agent and not self.modo_evaluacion:
                self.q_agent.registrar_partida(
                    resultado=resultado,
                    num_movimientos=self.movimientos_totales,
                    tiempo_partida=tiempo_partida,
                    recompensa_total=self.recompensa_total
                )
                self.q_agent.save_q_table()
            
            # Solo mostrar mensaje final si hay ventana (modo juego)
            if self.ventana:
                self.update()
                pygame.time.wait(500)
                self.end_game(tipo_final)

    def mostrar_estadisticas_consola(self):
        """Muestra las estadísticas del agente en la consola"""
        print("\n=== Comenzando partida contra la IA ===")
        print("\n=== Estadísticas Globales del Agente ===")
        stats = self.q_agent.obtener_estadisticas()
        print(f"Partidas Jugadas: {stats['total_partidas']}")
        print(f"Victorias: {stats['victorias']}")
        print(f"Derrotas: {stats['derrotas']}")
        print(f"Empates: {stats['empates']}")
        print(f"Tasa de Victorias: {stats['tasa_victorias']:.1f}%")
        print(f"Mov. Promedio: {stats['movimientos_promedio']:.1f}")
        #print(f"Tiempo Promedio por Partida: {stats['tiempo_promedio']:.1f}s")
        #print(f"Recompensa Promedio: {stats['recompensa_promedio']:.1f}")
        print("========================================")

def train_ai(episodes=10000):  # Aumentado para más experiencia
    """Entrena la IA jugando contra sí misma"""
    print(f"\nIniciando entrenamiento por {episodes} episodios...")
    game = Juego(ventana=None)  # Crear juego sin ventana para el entrenamiento
    game.entrenando = True  # Indicar que estamos entrenando
    game.modo_evaluacion = False  # Indicar que no estamos en modo evaluación
    ultimo_progreso = 0
    
    for episode in range(episodes):
        game.reset(mostrar_stats=False)  # Reiniciar sin mostrar estadísticas
        
        # Mostrar progreso cada vez que cambie el porcentaje
        progreso_actual = ((episode + 1) * 100) // episodes
        if progreso_actual > ultimo_progreso:
            ultimo_progreso = progreso_actual
            stats = game.q_agent.obtener_estadisticas()
            #print(f"\rProgreso: {progreso_actual}% - Tasa de victorias: {stats['tasa_victorias']:.1f}% - Recompensa: {stats['recompensa_promedio']:.1f}", end="")
            print(f"\rProgreso: {progreso_actual}% - Tasa de victorias: {stats['tasa_victorias']:.1f}%", end="")
        while not game.game_over:
            if game.turn == BLANCO:
                game.ai_move()
            else:
                # La IA juega contra sí misma
                current_state = game.tablero
                movimientos_posibles = game.get_all_possible_moves(ROJO)
                
                if not movimientos_posibles:
                    game.registrar_fin_juego("bloqueo", "victoria")
                    break
                
                # Usar el mismo agente para el otro jugador
                next_board = game.q_agent.get_action(current_state, movimientos_posibles)
                
                if next_board:
                    # Contar piezas antes del movimiento
                    piezas_antes = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                                     if current_state.get_pieza(fil, col) != 0)
                    
                    # Actualizar el tablero
                    game.tablero = next_board
                    game.movimientos_totales += 1
                    
                    # Contar piezas después del movimiento
                    piezas_despues = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                                       if game.tablero.get_pieza(fil, col) != 0)
                    
                    # Verificar si hubo captura
                    if piezas_antes > piezas_despues:
                        piezas_capturadas = piezas_antes - piezas_despues
                        game.capturas_rojas += piezas_capturadas
                        game.movimientos_sin_captura = 0
                    else:
                        game.movimientos_sin_captura += 1
                    
                    # Calcular recompensa (ya viene invertida para el oponente)
                    reward = calcular_recompensa(game.tablero, piezas_antes > piezas_despues, game.movimientos_sin_captura)
                    game.recompensa_total += reward
                    
                    next_possible_actions = game.get_all_possible_moves(ROJO)
                    game.q_agent.learn(current_state, next_board, reward, game.tablero, next_possible_actions)
                
                game.change_turn()
            
            # Evitar juegos infinitos - límite más flexible
            if game.movimientos_totales > 100:  # Aumentado de 100 a 150
                game.registrar_fin_juego("empate", "empate")
                break
    
    print("\n\nEntrenamiento completado!")
    
    # Guardar el progreso del entrenamiento
    game.q_agent.save_q_table()
    
    return game.q_agent

def main():
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTURA))
    pygame.display.set_caption('Damas')
    
    # Mostrar diálogo de entrenamiento
    train, episodes = show_training_dialog(ventana)
    
    # Crear juego
    game = Juego(ventana=True)
    
    if train:
        # Entrenar la IA sin mostrar estadísticas
        trained_agent = train_ai(episodes)
        game.q_agent = trained_agent
        game.entrenando = False  # Asegurarnos de que no estamos en modo entrenamiento
        game.modo_evaluacion = True  # Indicar que estamos en modo evaluación
        
        # Mostrar estadísticas solo al terminar el entrenamiento
        game.mostrar_estadisticas_consola()
    
    def mostrar_estadisticas():
        """Función auxiliar para mostrar las estadísticas"""
        print("\n=== Comenzando partida contra la IA ===")
        print("\n=== Estadísticas Globales del Agente ===")
        stats = game.q_agent.obtener_estadisticas()
        print(f"Partidas Jugadas: {stats['total_partidas']}")
        print(f"Victorias: {stats['victorias']}")
        print(f"Derrotas: {stats['derrotas']}")
        print(f"Empates: {stats['empates']}")
        print(f"Tasa de Victorias: {stats['tasa_victorias']:.1f}%")
        print(f"Mov. Promedio: {stats['movimientos_promedio']:.1f}")
        print(f"Tiempo Promedio por Partida: {stats['tiempo_promedio']:.1f}s")
        print(f"Recompensa Promedio: {stats['recompensa_promedio']:.1f}")
        print("========================================")
    
    # Bucle principal del juego
    running = True
    clock = pygame.time.Clock()
    
    while running:
        clock.tick(FPS)
        
        if game.turn == BLANCO and not game.game_over:
            game.ai_move()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                pos = pygame.mouse.get_pos()
                row, col = get_fil_col_from_mouse(pos)
                game.select(row, col)
                
            # Si se presiona el botón N, nueva partida
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    game.reset()
                    mostrar_estadisticas()  # Mostrar estadísticas al iniciar nueva partida
        
        game.update()
    
    pygame.quit()

def print_board_state(tablero):
    """Imprime el estado actual del tablero en la consola"""
    for fil in range(FILAS):
        row = []
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza == 0:
                row.append('.')
            else:
                if pieza.color == BLANCO:
                    row.append('B' if not pieza.king else 'K')
                else:
                    row.append('R' if not pieza.king else 'Q')
        print(' '.join(row))

def get_fil_col_from_mouse(pos):
    """Obtiene la fila y columna del tablero a partir de la posición del mouse"""
    x, y = pos
    fil = y // TAM_CASILLA
    col = x // TAM_CASILLA
    return fil, col

def show_training_dialog(ventana):
    font = pygame.font.Font(None, 36)
    text = font.render("¿Desea entrenar la IA antes de jugar?", True, TEXT)
    text_rect = text.get_rect(center=(ANCHO//2, ALTURA//2 - 80))

    # Input para episodios
    input_text = "1000"
    input_active = False
    input_rect = pygame.Rect((ANCHO//2 - 100), ALTURA//2 - 20, 200, 40)
    episodes_text = font.render("Episodios:", True, TEXT)
    episodes_rect = episodes_text.get_rect(midright=(input_rect.left - 10, input_rect.centery))

    # Crear botones
    button_width = 100
    button_height = 40
    button_margin = 20
    
    si_button = pygame.Rect((ANCHO//2 - button_width - button_margin), ALTURA//2 + 50, button_width, button_height)
    no_button = pygame.Rect((ANCHO//2 + button_margin), ALTURA//2 + 50, button_width, button_height)
    
    si_text = font.render("Sí", True, TEXT)
    no_text = font.render("No", True, TEXT)
    
    si_text_rect = si_text.get_rect(center=si_button.center)
    no_text_rect = no_text.get_rect(center=no_button.center)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if si_button.collidepoint(mouse_pos):
                    try:
                        episodes = max(1, min(10000, int(input_text)))
                        return True, episodes
                    except ValueError:
                        return True, 1000
                elif no_button.collidepoint(mouse_pos):
                    return False, 0
                elif input_rect.collidepoint(mouse_pos):
                    input_active = True
                else:
                    input_active = False
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isnumeric() and len(input_text) < 5:
                        input_text += event.unicode
                    
        ventana.fill((255, 255, 255))
        ventana.blit(text, text_rect)
        ventana.blit(episodes_text, episodes_rect)
        
        # Dibujar input
        color = AZUL if input_active else GRIS
        pygame.draw.rect(ventana, color, input_rect, 2)
        input_surface = font.render(input_text, True, TEXT)
        input_rect_text = input_surface.get_rect(center=input_rect.center)
        ventana.blit(input_surface, input_rect_text)
        
        # Dibujar botones
        pygame.draw.rect(ventana, GRIS, si_button)
        pygame.draw.rect(ventana, GRIS, no_button)
        ventana.blit(si_text, si_text_rect)
        ventana.blit(no_text, no_text_rect)
        
        pygame.display.update()

if __name__ == "__main__":
    main()
