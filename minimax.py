from copy import deepcopy
from constantes import *

def evaluate_board(tablero):
    score = 0
    for fil in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza != 0:
                # Valor de la pieza
                if pieza.color == BLANCO:
                    score += 1
                    if pieza.king:
                        score += 2  # Aumentar valor de las damas
                else:
                    score -= 1
                    if pieza.king:
                        score -= 2  # Aumentar valor de las damas
                
                # Valor basado en la posición
                if pieza.color == BLANCO:
                    score += (FILAS - fil) * 0.1  # Aumentar valor al acercarse al otro lado
                else:
                    score -= fil * 0.1  # Aumentar valor al acercarse al otro lado
                
                # Valor basado en la movilidad
                movimientos = tablero.get_movimientos_validos(pieza)
                score += len(movimientos) * 0.05 if pieza.color == BLANCO else -len(movimientos) * 0.05
    return score

def minimax(tablero, profundidad, maximizando_jugador):
    if profundidad == 0 or tablero.ganador() is not None:
        return evaluate_board(tablero)
    
    if maximizando_jugador:
        max_eval = float('-inf')
        for movimiento in obtener_movimientos_posibles(tablero, BLANCO):
            evaluacion = minimax(movimiento, profundidad - 1, False)
            max_eval = max(max_eval, evaluacion)
        return max_eval
    else:
        min_eval = float('inf')
        for movimiento in obtener_movimientos_posibles(tablero, ROJO):
            evaluacion = minimax(movimiento, profundidad - 1, True)
            min_eval = min(min_eval, evaluacion)
        return min_eval

def obtener_movimientos_posibles(tablero, color):
    movimientos = []
    for fil in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero.get_pieza(fil, col)
            if pieza != 0 and pieza.color == color:
                movimientos_validos = tablero.get_movimientos_validos(pieza)
                for move, skipped in movimientos_validos.items():
                    new_tablero = deepcopy(tablero)
                    new_pieza = new_tablero.get_pieza(pieza.fil, pieza.col)
                    new_tablero.move(new_pieza, move[0], move[1])
                    if skipped:
                        new_tablero.eliminar(skipped)
                    movimientos.append(new_tablero)
    return movimientos
