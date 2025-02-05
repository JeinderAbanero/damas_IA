import numpy as np
import pickle
import os
from constantes import *

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):  
        self.alpha = alpha  
        self.gamma = gamma  
        self.epsilon = epsilon  
        self.min_epsilon = 0.01  
        self.epsilon_decay = 0.9999  
        self.q_table = {}  
        self.victorias = 0
        self.derrotas = 0
        self.empates = 0
        self.historial_recompensas = []
        self.historial_movimientos = []
        self.tiempo_promedio_partida = 0
        self.total_partidas = 0
        self.partidas_desde_ultimo_ajuste = 0
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
        """Selecciona una acción usando la política epsilon-greedy mejorada"""
        state = self.get_state_key(tablero)
        
        # Decaimiento de epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        # Exploración inteligente: favorecer movimientos de captura
        if np.random.random() < self.epsilon:
            movimientos_captura = [m for m in movimientos_posibles if self.es_movimiento_captura(tablero, m)]
            if movimientos_captura:
                return np.random.choice(movimientos_captura)
            return np.random.choice(movimientos_posibles)
        
        # Explotación con preferencia por capturas
        return self.get_best_action(state, movimientos_posibles, tablero)

    def es_movimiento_captura(self, tablero_actual, tablero_siguiente):
        """Determina si un movimiento es de captura contando piezas"""
        piezas_antes = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                          if tablero_actual.get_pieza(fil, col) != 0)
        piezas_despues = sum(1 for fil in range(FILAS) for col in range(COLUMNAS) 
                            if tablero_siguiente.get_pieza(fil, col) != 0)
        return piezas_antes > piezas_despues

    def get_best_action(self, state, movimientos_posibles, tablero_actual):
        """Obtiene la mejor acción con preferencia por capturas"""
        if not movimientos_posibles:
            return None

        if state not in self.q_table:
            self.q_table[state] = {}

        # Separar movimientos de captura y no captura
        movimientos_captura = []
        movimientos_normales = []
        
        for action in movimientos_posibles:
            if self.es_movimiento_captura(tablero_actual, action):
                movimientos_captura.append(action)
            else:
                movimientos_normales.append(action)

        best_value = float('-inf')
        best_action = None

        # Priorizar movimientos de captura
        movimientos_a_evaluar = movimientos_captura + movimientos_normales
        
        for action in movimientos_a_evaluar:
            action_key = self.get_action_key(action)
            if action_key not in self.q_table[state]:
                # Inicializar con valor más alto para capturas
                initial_value = 1.0 if action in movimientos_captura else 0.0
                self.q_table[state][action_key] = initial_value
            
            current_value = self.q_table[state][action_key]
            # Bonus para movimientos de captura
            if action in movimientos_captura:
                current_value *= 1.2  # 20% bonus para capturas
            
            if current_value > best_value:
                best_value = current_value
                best_action = action

        return best_action or np.random.choice(movimientos_posibles)

    def get_action_key(self, tablero):
        """Convierte una acción (tablero resultante) en una cadena única"""
        return self.get_state_key(tablero)

    def learn(self, state, action, reward, next_state, next_possible_actions):
        """Actualiza la tabla Q con aprendizaje mejorado"""
        state_key = self.get_state_key(state)
        action_key = self.get_action_key(action)
        next_state_key = self.get_state_key(next_state)

        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action_key not in self.q_table[state_key]:
            self.q_table[state_key][action_key] = 0.0

        # Calcular el valor Q máximo para el siguiente estado con bonus por capturas
        next_max = 0
        if next_possible_actions:
            next_values = []
            if next_state_key in self.q_table:
                for next_action in next_possible_actions:
                    next_action_key = self.get_action_key(next_action)
                    if next_action_key in self.q_table[next_state_key]:
                        value = self.q_table[next_state_key][next_action_key]
                        if self.es_movimiento_captura(next_state, next_action):
                            value *= 1.2  # Bonus para capturas futuras
                        next_values.append(value)
            if next_values:
                next_max = max(next_values)

        # Actualizar el valor Q con mayor peso en recompensas positivas
        current_q = self.q_table[state_key][action_key]
        new_q = current_q + self.alpha * (reward + self.gamma * next_max - current_q)
        
        # Ajuste adicional para favorecer estados ganadores
        if reward > 0:
            new_q *= 1.1  # 10% extra para recompensas positivas
        
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

def calcular_recompensa(tablero, movimiento_captura, movimientos_sin_captura):
    """Calcula la recompensa para un estado dado"""
    recompensa = 0
    
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
                else:
                    piezas_blancas += 1
                    if pieza.king:
                        reyes_blancos += 1

    # Recompensa base por diferencia de piezas
    diferencia_piezas = piezas_rojas - piezas_blancas
    recompensa += diferencia_piezas * 25

    # Recompensa por reyes
    diferencia_reyes = reyes_rojos - reyes_blancos
    recompensa += diferencia_reyes * 40

    # Recompensa agresiva por captura
    if movimiento_captura:
        recompensa += 50
        if movimientos_sin_captura < 5:
            recompensa += 30  # Bonus por mantener presión

    # Penalización por inactividad
    if movimientos_sin_captura > 5:
        recompensa -= (movimientos_sin_captura - 5) * 10

    # Bonus por posición y avance
    for fil in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza != 0 and pieza.color == ROJO:
                if not pieza.king:
                    # Bonus por avance
                    recompensa += (FILAS - fil - 1) * 5
                    
                    # Bonus por proximidad a coronación
                    if fil >= FILAS - 2:
                        recompensa += 20
                else:
                    # Bonus por control del centro
                    if 1 <= fil <= FILAS-2 and 1 <= col <= COLUMNAS-2:
                        recompensa += 15

    # Victoria/Derrota
    if piezas_rojas > 0 and piezas_blancas == 0:  # Victoria
        recompensa += 200
        if movimientos_sin_captura < 20:  # Victoria rápida
            recompensa += (20 - movimientos_sin_captura) * 5
        if piezas_rojas >= 2:  # Victoria dominante
            recompensa += piezas_rojas * 20
    elif piezas_rojas == 0 and piezas_blancas > 0:  # Derrota
        recompensa -= 200
        recompensa -= piezas_blancas * 10

    # Penalización por tendencia al empate
    if movimientos_sin_captura >= 10:
        recompensa -= (movimientos_sin_captura - 9) * 15

    return -recompensa
