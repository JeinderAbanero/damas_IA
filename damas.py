import pygame

# Constantes 

ANCHO, ALTURA = 600, 600
FILAS, COLUMNAS = 4, 4 
TAM_CASILLA = ANCHO // COLUMNAS

# Colores 

ROJO = (255, 105, 97)
BLANCO = (224, 176, 255)
NEGRO = (20, 20, 20)
GRIS = (128,128,128)
AZUL = (59, 131, 189)

CORONA = pygame.transform.scale(pygame.image.load("corona.png"), (45, 25))

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
        radio = TAM_CASILLA//2 - self.RELLENO
        pygame.draw.circle(win,GRIS,(self.x, self.y),radio + self.BORDE)
        pygame.draw.circle(win,self.color,(self.x, self.y),radio)
        if self.king:
            win.blit(CORONA, (self.x - CORONA.get_width()//2, self.y - CORONA.get_height()//2))
    def move (self, fil, col):
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
    
    def draw_cuadrados(self,win): # ORDEN: rojo, blanco, rojo, blanco, rojo...
        win.fill(NEGRO)
        for fil in range (FILAS):
            for col in range(fil%2, COLUMNAS, 2):
                pygame.draw.rect(win, ROJO,(fil*TAM_CASILLA, col * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA))
                #fila, columna, ancho alto
    
    def move(self, pieza, fil, col):
        self.tablero[pieza.fil][pieza.col], self.tablero[fil][col] = self.tablero[fil][col], self.tablero[pieza.fil][pieza.col] 
        pieza.move(fil, col)

        if fil == FILAS - 1 or fil == 0:
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
                        self.tablero[fil].append(Piezas(fil,col,BLANCO))
                    elif fil > 2:
                        self.tablero[fil].append(Piezas(fil,col, ROJO))
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
    
    def ganador (self):
        if self.ROJO_left <= 0:
            return BLANCO
        elif self.BLANCO_left <= 0:
            return ROJO
        return None
    def get_movimientos_validos(self, pieza):
        movimientos = {}
        izq = pieza.col - 1
        der = pieza.col + 1
        fil = pieza.fil

        if pieza.color == ROJO or pieza.king: #Verifico la dirección en la que se pueden mover las piezas.
            movimientos.update(self.atravezar_izq(fil -1, max(fil-3, -1), -1, pieza.color, izq))
            movimientos.update(self.atravezar_der(fil -1, max(fil-3, -1), -1, pieza.color, der))
        #Se actualizan los movimientos con lo que se devuelva de ahí.
        if pieza.color == BLANCO or pieza.king:
            movimientos.update(self.atravezar_izq(fil +1, min(fil+3, FILAS), 1, pieza.color, izq))
            movimientos.update(self.atravezar_der(fil +1, min(fil+3, FILAS), 1, pieza.color, der))
        #Se actualizan los movimientos con lo que se devuelva de ahí.
        return movimientos
    
    def atravezar_izq(self, start, stop, step, color, izq, skipped=[]):
        movimientos = {}  # Siempre inicializamos un diccionario vacío
        last = []
        for f in range(start, stop, step):  # F = Fila
            if izq < 0:
                break
            
            current = self.tablero[f][izq]
            if current == 0:  # Hay un cuadrado vacío
                if skipped and not last:
                    break  # No hay lugar donde moverse.
                elif skipped:  # Verificar si se ha saltado.
                    movimientos[(f, izq)] = last + skipped  # Situación de salto.
                else:  # Se agrega como posible movimiento a las otras casillas.
                    movimientos[(f, izq)] = last
                if last:
                    if step == -1:
                        fil = max(f - 3, 0)
                    else:
                        fil = min(f + 3, FILAS)
                    movimientos.update(self.atravezar_izq(f + step, fil, step, color, izq - 1, skipped=last))
                    movimientos.update(self.atravezar_der(f + step, fil, step, color, izq + 1, skipped=last))
                break
            elif current.color == color:  # No me puedo mover a un lugar que está ocupado.
                break
            else:
                last = [current]  # De ser el color contrario, podría moverse sobre él (asumiéndolo como 'vacío').
            izq -= 1
        
        # Aseguramos que siempre retornamos un diccionario
        return movimientos

    
    def atravezar_der(self, start, stop, step, color, der, skipped=[]):
        movimientos = {}
        last = []
        for f in range(start, stop, step): #F = Fila
            if der >= COLUMNAS:
                break
            current = self. tablero[f] [der]
            if current == 0: #Hay un cuadrado vacío.
                if skipped and not last:
                    break #No hay lugar donde moverse.
                elif skipped: #Verificar si se ha saltado.
                    movimientos[(f,der)] = last + skipped #Situación de salto.
                else: #Se agrega como posible movimiento a las otras casillas.
                    movimientos[(f, der)] = last
                if last:
                    if step == - 1:
                        fil = max(f-3, 0)
                    else:
                        fil = min(f+3, FILAS)
                        movimientos.update(self.atravezar_izq(f+step, fil, step, color, der-1, skipped=last))
                        movimientos.update(self.atravezar_der(f+step, fil, step, color, der+1, skipped=last))
                break
            elif current.color == color: #No me puedo mover a un lugar que está ocupado.
                break
            else:
                last = [current] #De ser el color contrario, podría moverse sobre él (asumiéndolo como 'vacio').
            der += 1
        return movimientos



#MANEJO DEL JUEGO
#¿De quién es el turno? ¿ seleccioné una pieza? ¿ puedo moverme a x lugar?
class Juego:
    def __init__(self, win):
        self ._init() #Se puso en otra función ya que se utiliza casi lo mismo para el método de reinicio.
        self.win = win
    def update(self): #Update (actualización) de la pantalla del Pygame.
        self.tablero.draw(self.win)
        self.draw_movimientos_validos(self.movimientos_validos)
        pygame.display.update()
    def _init(self):
        self.selected = None
        self.tablero = Tablero()
        self.turn = BLANCO
        self.movimientos_validos = {}
    def ganador(self):
        return self. tablero.ganador()
    def reset(self): #Método para reiniciar el juego.
        self ._init()
    def select(self, fil, col):
        if self.selected:
            result = self._move(fil, col)  # Se mueve lo seleccionado.
            if not result:
                self.selected = None
                self.select(fil, col)
        pieza = self.tablero.get_pieza(fil, col)
        print(f"Seleccionada: {pieza}")  # Depuración
        if pieza != 0 and pieza.color == self.turn:
            self.selected = pieza
            self.movimientos_validos = self.tablero.get_movimientos_validos(pieza)
            print(f"Movimientos válidos: {self.movimientos_validos}")  # Depuración
            return True
        return False

    
    def _move(self, fil, col):
        pieza = self.tablero.get_pieza(fil, col)
        
        if self.selected and pieza == 0 and (fil, col) in self.movimientos_validos:
            # Mostrar el movimiento de la pieza (origen -> destino)
            print(f"Pieza movida: {self.selected.color} desde ({self.selected.fil}, {self.selected.col}) a ({fil}, {col})")
            
            # Mover la pieza
            self.tablero.move(self.selected, fil, col)
            
            skipped = self.movimientos_validos[(fil, col)]
            if skipped:
                self.tablero.eliminar(skipped)
            
            # Cambiar de turno
            self.change_turn()
        else:
            return False
        return True


    
    def draw_movimientos_validos(self, movimientos):
        for move in movimientos:
            fil, col = move
            pygame.draw.circle(self.win, AZUL, (col * TAM_CASILLA + TAM_CASILLA // 2, fil * TAM_CASILLA + TAM_CASILLA //2), 15)
    
    def change_turn(self):
        self.movimientos_validos = {}
        if self.turn == ROJO:
            self.turn = BLANCO
        else:
            self.turn = ROJO

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
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                fil, col = get_fil_col_from_mouse(pos)
                game.select(fil, col)
        game.update()
    pygame.quit()
main()







