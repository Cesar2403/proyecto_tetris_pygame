import pygame
import random

FORMAS = [
    [[1, 1, 1, 1]],  # linea
    [[1, 0, 0], [1, 1, 1]],  # L invertida
    [[0, 0, 1], [1, 1, 1]],  # L normal
    [[1, 1], [1, 1]],  # bloque
    [[0, 1, 1], [1, 1, 0]],  # forma de s normal
    [[0, 1, 0], [1, 1, 1]],  # letra T corta
    [[1, 1, 0], [0, 1, 1]]  # forma de s invertida
]

ANCHO_PANTALLA = 300
ALTO_PANTALLA = 600
TAMANO_BLOQUE = 30
COLUMNAS = ANCHO_PANTALLA // TAMANO_BLOQUE
FILAS = ALTO_PANTALLA // TAMANO_BLOQUE

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
clock = pygame.time.Clock()
pygame.display.set_caption("Pygame Tetris")

tablero = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]
forma_pieza = random.choice(FORMAS)
x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
y_pieza = 0
color_pieza = ("blue")
velocidad_caida = 1.5
tiempo_anterior = pygame.time.get_ticks()
intervalo_movimiento = 200
tiempo_ultima_rotacion = 0
delay_rotacion = 200
espacio_presionado_anteriormente = False


def crear_pieza():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                pygame.draw.rect(pantalla, color_pieza,
                                 ((x_pieza + j) * TAMANO_BLOQUE,
                                  (y_pieza + i) * TAMANO_BLOQUE,
                                  TAMANO_BLOQUE, TAMANO_BLOQUE))


def crear_recuadro():
    for x in range(0, ANCHO_PANTALLA, TAMANO_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (x, 0), (x, ALTO_PANTALLA))
    for y in range(0, ALTO_PANTALLA, TAMANO_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (0, y), (ANCHO_PANTALLA, y))


def colision():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                if (y_pieza + i >= FILAS or
                        x_pieza + j < 0 or
                        x_pieza + j >= COLUMNAS or
                        tablero[y_pieza + i][x_pieza + j]):
                    return True
    return False


def colocar_pieza():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda and y_pieza + i >= 0:
                tablero[y_pieza + i][x_pieza + j] = color_pieza
    return eliminar_filas_completas()


def nueva_pieza():
    global forma_pieza, x_pieza, y_pieza
    forma_pieza = random.choice(FORMAS)
    x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
    y_pieza = 0
    if colision():
        return False
    return True


def rotar_pieza():
    global forma_pieza, tiempo_ultima_rotacion
    momento_actual = pygame.time.get_ticks()
    if momento_actual - tiempo_ultima_rotacion < delay_rotacion:
        return
    filas = len(forma_pieza)
    columnas = len(forma_pieza[0])
    rotada = [[forma_pieza[filas - 1 - i][j] for i in range(filas)] for j in range(columnas)]
    forma_vieja = forma_pieza
    forma_pieza = rotada
    if not colision():
        tiempo_ultima_rotacion = momento_actual
    else:
        forma_pieza = forma_vieja


# dsdssjfkdjfs
def eliminar_filas_completas():
    eliminadas = 0
    for y in range(FILAS - 1, -1, -1):
        linea_completa = True
        for x in range(COLUMNAS):
            if not tablero[y][x]:
                linea_completa = False
                break
        if linea_completa:
            eliminadas += 1
            for y2 in range(y, 0, -1):
                tablero[y2] = tablero[y2 - 1].copy()
            tablero[0] = [0] * COLUMNAS
    return eliminadas


def main():
    global x_pieza, y_pieza, tiempo_anterior

    running = True
    while running:
        pantalla.fill("BLACK")
        crear_recuadro()

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - tiempo_anterior > 1000 / velocidad_caida:
            y_pieza += 1
            tiempo_anterior = tiempo_actual
            if colision():
                y_pieza -= 1
                filas_eliminadas = colocar_pieza()
                if not nueva_pieza():
                    running = False

        elif tiempo_actual - tiempo_anterior > 1000 / velocidad_caida:
            y_pieza += 1
            tiempo_anterior = tiempo_actual
            if colision():
                y_pieza -= 1
                filas_eliminadas = colocar_pieza()
                if not nueva_pieza():
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if tiempo_actual - tiempo_anterior > intervalo_movimiento:
            if keys[pygame.K_LEFT] and x_pieza > 0:
                x_pieza -= 1
                tiempo_anterior = tiempo_actual
                if colision():
                    x_pieza += 1

            if keys[pygame.K_RIGHT] and x_pieza < COLUMNAS - len(forma_pieza[0]):
                x_pieza += 1
                tiempo_anterior = tiempo_actual
                if colision():
                    x_pieza -= 1

        if keys[pygame.K_DOWN]:
            y_pieza += 1
            if colision():
                y_pieza -= 1
                filas_eliminadas = colocar_pieza()
                if not nueva_pieza():
                    running = False

        if keys[pygame.K_SPACE]:
            if not espacio_presionado_anteriormente:  # Si justo ahora se presionó la tecla
                while not colision():
                    y_pieza += 1
                y_pieza -= 1

                filas_eliminadas = colocar_pieza()
                if not nueva_pieza():
                    running = False

                tiempo_anterior = pygame.time.get_ticks()

            espacio_presionado_anteriormente = True
        else:
            espacio_presionado_anteriormente = False

        if keys[pygame.K_UP]:
            rotar_pieza()

        for y in range(FILAS):
            for x in range(COLUMNAS):
                if tablero[y][x]:
                    pygame.draw.rect(pantalla, tablero[y][x],
                                     (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE,
                                      TAMANO_BLOQUE, TAMANO_BLOQUE))

        crear_pieza()
        pygame.display.flip()
        clock.tick(60)


main()
pygame.quit()

