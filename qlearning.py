import numpy as np
import pickle
import os
from constantes import *

class QLearningAgent:
    def __init__(self, alpha=0.15, gamma=0.95, epsilon=0.15):  
        self.alpha = alpha  
        self.gamma = gamma  
        self.epsilon = epsilon  
        self.q_table = {}  
        self.victorias = 0
        self.derrotas = 0
        self.empates = 0
        self.historial_recompensas = []
        self.historial_movimientos = []
        self.tiempo_promedio_partida = 0
        self.total_partidas = 0
        self.load_q_table()

    def get_state_key(self, tablero):
        """Convierte el estado del tablero en una cadena única"""
        state = []
        for fil in range(FILAS):
            for col in range(COLUMNAS):
                pieza = tablero.tablero[fil][col]
                if pieza == 0:
                    state.append('0')
                else:
                    # Representa el color y si es rey
                    value = '1' if pieza.color == BLANCO else '2'
                    value += 'K' if pieza.king else 'N'
                    state.append(value)
        return ','.join(state)

    def get_action(self, tablero, movimientos_posibles):
        """Selecciona una acción usando la política epsilon-greedy"""
        state = self.get_state_key(tablero)
        
        # Exploración: elegir un movimiento aleatorio
        if np.random.random() < self.epsilon:
            return np.random.choice(movimientos_posibles)
        
        # Explotación: elegir el mejor movimiento conocido
        return self.get_best_action(state, movimientos_posibles)

    def get_best_action(self, state, movimientos_posibles):
        """Obtiene la mejor acción para un estado dado"""
        if not movimientos_posibles:
            return None

        # Si el estado no está en la tabla Q, inicializarlo
        if state not in self.q_table:
            self.q_table[state] = {}

        best_value = float('-inf')
        best_action = np.random.choice(movimientos_posibles)  # Por defecto, elegir uno aleatorio

        for action in movimientos_posibles:
            action_key = self.get_action_key(action)
            if action_key not in self.q_table[state]:
                self.q_table[state][action_key] = 0.0
            
            if self.q_table[state][action_key] > best_value:
                best_value = self.q_table[state][action_key]
                best_action = action

        return best_action

    def get_action_key(self, tablero):
        """Convierte una acción (tablero resultante) en una cadena única"""
        return self.get_state_key(tablero)

    def learn(self, state, action, reward, next_state, next_possible_actions):
        """Actualiza la tabla Q basándose en la recompensa recibida"""
        state_key = self.get_state_key(state)
        action_key = self.get_action_key(action)
        next_state_key = self.get_state_key(next_state)

        # Inicializar valores si no existen
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action_key not in self.q_table[state_key]:
            self.q_table[state_key][action_key] = 0.0

        # Calcular el valor Q máximo para el siguiente estado
        next_max = 0
        if next_possible_actions:
            next_values = []
            if next_state_key in self.q_table:
                for next_action in next_possible_actions:
                    next_action_key = self.get_action_key(next_action)
                    if next_action_key in self.q_table[next_state_key]:
                        next_values.append(self.q_table[next_state_key][next_action_key])
            if next_values:
                next_max = max(next_values)

        # Actualizar el valor Q
        current_q = self.q_table[state_key][action_key]
        new_q = current_q + self.alpha * (reward + self.gamma * next_max - current_q)
        self.q_table[state_key][action_key] = new_q

    def registrar_partida(self, resultado, num_movimientos, tiempo_partida, recompensa_total):
        """Registra el resultado de una partida y actualiza las estadísticas"""
        self.total_partidas += 1
        self.historial_movimientos.append(num_movimientos)
        self.historial_recompensas.append(recompensa_total)
        
        # Actualizar victorias/derrotas/empates
        if resultado == "victoria":
            self.victorias += 1
        elif resultado == "derrota":
            self.derrotas += 1
        else:  # empate
            self.empates += 1
            
        # Actualizar tiempo promedio
        if self.tiempo_promedio_partida == 0:
            self.tiempo_promedio_partida = tiempo_partida
        else:
            self.tiempo_promedio_partida = (self.tiempo_promedio_partida * (self.total_partidas - 1) + 
                                          tiempo_partida) / self.total_partidas
    
    def obtener_estadisticas(self):
        """Devuelve las estadísticas actuales del agente"""
        if self.total_partidas == 0:
            return {
                "total_partidas": 0,
                "victorias": 0,
                "derrotas": 0,
                "empates": 0,
                "tasa_victorias": 0.0,
                "recompensa_promedio": 0.0,
                "movimientos_promedio": 0.0,
                "tiempo_promedio": 0.0,
                "ultimas_recompensas": [],
                "ultimos_movimientos": []
            }
            
        return {
            "total_partidas": self.total_partidas,
            "victorias": self.victorias,
            "derrotas": self.derrotas,
            "empates": self.empates,
            "tasa_victorias": (self.victorias / self.total_partidas) * 100,
            "recompensa_promedio": sum(self.historial_recompensas) / len(self.historial_recompensas) if self.historial_recompensas else 0,
            "movimientos_promedio": sum(self.historial_movimientos) / len(self.historial_movimientos) if self.historial_movimientos else 0,
            "tiempo_promedio": self.tiempo_promedio_partida,
            "ultimas_recompensas": self.historial_recompensas[-10:] if self.historial_recompensas else [],
            "ultimos_movimientos": self.historial_movimientos[-10:] if self.historial_movimientos else []
        }

    def mostrar_estadisticas_consola(self):
        """Muestra las estadísticas del agente en la consola"""
        stats = self.obtener_estadisticas()
        
        print("\n=== Estadísticas Globales del Agente ===")
        print(f"Partidas Jugadas: {stats['total_partidas']}")
        print(f"Victorias: {stats['victorias']}")
        print(f"Derrotas: {stats['derrotas']}")
        print(f"Empates: {stats['empates']}")
        print(f"Tasa de Victorias: {stats['tasa_victorias']:.1f}%")
        print(f"Movimientos Promedio: {stats['movimientos_promedio']:.1f}")
        print(f"Tiempo Promedio por Partida: {stats['tiempo_promedio']:.1f}s")
        print(f"Recompensa Promedio: {stats['recompensa_promedio']:.1f}")
        print("=" * 40)

    def save_q_table(self):
        """Guarda la tabla Q y las estadísticas en archivos"""
        # Guardar tabla Q
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)
        
        # Guardar estadísticas
        estadisticas = {
            'victorias': self.victorias,
            'derrotas': self.derrotas,
            'empates': self.empates,
            'historial_recompensas': self.historial_recompensas,
            'historial_movimientos': self.historial_movimientos,
            'tiempo_promedio_partida': self.tiempo_promedio_partida,
            'total_partidas': self.total_partidas
        }
        with open('estadisticas.pkl', 'wb') as f:
            pickle.dump(estadisticas, f)

    def load_q_table(self):
        """Carga la tabla Q y las estadísticas desde archivos si existen"""
        if os.path.exists('q_table.pkl'):
            with open('q_table.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
        
        if os.path.exists('estadisticas.pkl'):
            with open('estadisticas.pkl', 'rb') as f:
                estadisticas = pickle.load(f)
                self.victorias = estadisticas['victorias']
                self.derrotas = estadisticas['derrotas']
                self.empates = estadisticas['empates']
                self.historial_recompensas = estadisticas['historial_recompensas']
                self.historial_movimientos = estadisticas['historial_movimientos']
                self.tiempo_promedio_partida = estadisticas['tiempo_promedio_partida']
                self.total_partidas = estadisticas['total_partidas']

def calcular_recompensa(tablero, movimiento_captura):
    """Calcula la recompensa para un estado dado"""
    recompensa = 10  # Recompensa base aumentada para 4x4
    
    # Recompensa por capturar piezas (más alta en 4x4 porque hay menos piezas)
    if movimiento_captura:
        recompensa += 100  # Aumentada porque cada pieza es más valiosa en 4x4
    
    # Contar piezas y reyes
    piezas_rojas = 0
    piezas_blancas = 0
    reyes_rojos = 0
    reyes_blancos = 0
    
    for fil in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza != 0:
                if pieza.color == ROJO:
                    piezas_rojas += 1
                    if pieza.king:
                        reyes_rojos += 1
                        recompensa += 50  # Aumentado porque en 4x4 los reyes son más valiosos
                else:
                    piezas_blancas += 1
                    if pieza.king:
                        reyes_blancos += 1
    
    # Recompensa por ventaja de piezas (más alta porque hay menos piezas)
    diferencia_piezas = piezas_rojas - piezas_blancas
    recompensa += diferencia_piezas * 60  # Duplicado porque cada pieza es más importante
    
    # Recompensa por posición
    for fil in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza != 0 and pieza.color == ROJO:
                if not pieza.king:
                    # Recompensa por avanzar hacia el lado contrario
                    # En 4x4 el avance es más importante porque hay menos filas
                    recompensa += (FILAS - fil - 1) * 10  # Triplicado para 4x4
    
                    # Bonus por estar cerca de convertirse en rey
                    # En 4x4, esto es cuando fil >= 2
                    if fil >= FILAS - 2:
                        recompensa += 40  # Duplicado porque coronar es más fácil/importante en 4x4
                else:
                    # Los reyes reciben bonus por estar en el centro del tablero
                    # En 4x4 el control del centro es más crítico
                    distancia_centro = abs(col - COLUMNAS//2) + abs(fil - FILAS//2)
                    recompensa += (4 - distancia_centro) * 15  # Triplicado para 4x4
    
    # Penalizaciones y bonificaciones adicionales
    if piezas_rojas < piezas_blancas:  # Si estamos en desventaja
        recompensa -= 20  # Duplicada la penalización
    
    if piezas_rojas > 0 and piezas_blancas == 0:  # Victoria
        recompensa += 500  # Aumentada porque ganar en 4x4 es más significativo
    
    return recompensa
