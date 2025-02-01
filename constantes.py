import os
import sys
import pygame

# Constantes de dimensiones
ANCHO, ALTURA = 600, 600
FILAS, COLUMNAS = 4, 4 
TAM_CASILLA = ANCHO // COLUMNAS
FPS = 60

# Constante para el máximo de movimientos sin captura antes de declarar empate
MAX_MOVIMIENTOS_SIN_CAPTURA = 64

# Colores
ROJO = (255, 105, 97)
ROJO_TAB = (255, 0, 0)
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
GRIS = (128, 128, 128)
AZUL = (59, 131, 189)
TEXT = (0, 0, 0)

def resource_path(relative_path):
    """Obtiene la ruta del archivo en el ejecutable"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Cargar imagen de corona
corona_img_path = resource_path("corona.png")
CORONA = pygame.transform.scale(pygame.image.load(corona_img_path), (45, 25))

def color_to_name(color):
    """Convierte un color a su nombre correspondiente"""
    if color == ROJO:
        return 'ROJO'
    elif color == BLANCO:
        return 'BLANCO'
    return 'Desconocido'

def dividir_texto(text, font, max_width):
    """Divide un texto en líneas según el ancho máximo"""
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
