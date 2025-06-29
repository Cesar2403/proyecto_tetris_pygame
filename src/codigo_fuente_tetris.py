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

# Colores para cada pieza
colores_piezas = {
    0: (0, 255, 255),
    1: (255, 165, 0),
    2: (0, 0, 255),
    3: (255, 255, 0),
    4: (0, 255, 0),
    5: (160, 32, 240),
    6: (255, 0, 0),
}

COLUMNAS_TABLERO = 10
FILAS = 20
TAMANO_BLOQUE = 30
ANCHO_TABLERO = COLUMNAS_TABLERO * TAMANO_BLOQUE  # 300 px
ALTO_PANTALLA = FILAS * TAMANO_BLOQUE  # 600 px
ESPACIO_LATERAL = 150
MARGEN_IZQUIERDO = 200
ANCHO_PANTALLA = MARGEN_IZQUIERDO + ANCHO_TABLERO + ESPACIO_LATERAL

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
tablero = [[None for _ in range(COLUMNAS_TABLERO)] for _ in range(FILAS)]
clock = pygame.time.Clock()
pygame.display.set_caption("Pygame Tetris")

tablero = [[None for _ in range(COLUMNAS_TABLERO)] for _ in range(FILAS)]
indice_pieza_actual = random.randint(0, len(FORMAS) - 1)
forma_pieza = FORMAS[indice_pieza_actual]
x_pieza = COLUMNAS_TABLERO // 2 - len(forma_pieza[0]) // 2
y_pieza = 0
velocidad_caida = 1.5
tiempo_caida = pygame.time.get_ticks()
tiempo_movimiento_horizontal = pygame.time.get_ticks()
intervalo_movimiento = 200
tiempo_ultima_rotacion = 0
delay_rotacion = 200
espacio_presionado_anteriormente = False
pieza_guardada = None
pieza_guardada_este_turno = False
pausado = False
puntos = 0
back_to_back = False
bonus_back_to_back = 0.5
nivel = 1
puntos_siguiente_nivel = 1000
velocidad_caida = 1.0
indice_pieza_siguiente = random.randint(0, len(FORMAS) - 1)
mostrar_back_to_back = False


def crear_pieza():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                x = MARGEN_IZQUIERDO + (x_pieza + j) * TAMANO_BLOQUE
                y = (y_pieza + i) * TAMANO_BLOQUE
                pygame.draw.rect(pantalla, colores_piezas[indice_pieza_actual], (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, (0, 0, 0), (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)


def crear_recuadro():
    for x in range(0, ANCHO_TABLERO + 1, TAMANO_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (x + MARGEN_IZQUIERDO, 0), (x + MARGEN_IZQUIERDO, ALTO_PANTALLA))
    for y in range(0, ALTO_PANTALLA + 1, TAMANO_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (MARGEN_IZQUIERDO, y), (MARGEN_IZQUIERDO + ANCHO_TABLERO, y))


def colision():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                ny = y_pieza + i
                nx = x_pieza + j
                if nx < 0 or nx >= COLUMNAS_TABLERO:
                    return True
                if ny >= FILAS:
                    return True
                if ny >= 0 and tablero[ny][nx] is not None:
                    return True
    return False


def colocar_pieza():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda and y_pieza + i >= 0:
                tablero[y_pieza + i][x_pieza + j] = indice_pieza_actual
    return eliminar_filas_completas()


def nueva_pieza():
    global forma_pieza, x_pieza, y_pieza, indice_pieza_actual, ya_se_guardo_esta_vuelta, indice_pieza_siguiente

    indice_pieza_actual = indice_pieza_siguiente
    forma_pieza = FORMAS[indice_pieza_actual]
    x_pieza = COLUMNAS_TABLERO // 2 - len(forma_pieza[0]) // 2
    y_pieza = 0
    ya_se_guardo_esta_vuelta = False

    indice_pieza_siguiente = random.randint(0, len(FORMAS) - 1)

    if colision():
        return False
    return True


def rotar_pieza():
    global forma_pieza, tiempo_ultima_rotacion, x_pieza

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
        x_pieza -= 1
        if not colision():
            tiempo_ultima_rotacion = momento_actual
            return
        x_pieza += 2
        if not colision():
            tiempo_ultima_rotacion = momento_actual
            return
        x_pieza -= 1
        forma_pieza = forma_vieja


def eliminar_filas_completas():
    eliminadas = 0
    y = FILAS - 1
    while y >= 0:
        linea_completa = True
        for x in range(COLUMNAS_TABLERO):
            if tablero[y][x] is None:
                linea_completa = False
                break
        if linea_completa:
            eliminadas += 1
            for y2 in range(y, 0, -1):
                tablero[y2] = tablero[y2 - 1].copy()
            tablero[0] = [None] * COLUMNAS_TABLERO
            y += 1
        y -= 1
    return eliminadas


def guardar_pieza():
    global pieza_guardada, forma_pieza, indice_pieza_actual, x_pieza, y_pieza, pieza_guardada_este_turno

    if pieza_guardada_este_turno:
        return

    if pieza_guardada is None:
        pieza_guardada = indice_pieza_actual
        if not nueva_pieza():
            pygame.quit()
            exit()
    else:
        pieza_guardada, indice_pieza_actual = indice_pieza_actual, pieza_guardada
        forma_pieza = FORMAS[indice_pieza_actual]
        x_pieza = COLUMNAS_TABLERO // 2 - len(forma_pieza[0]) // 2
        y_pieza = 0
        if colision():
            pygame.quit()
            exit()

    pieza_guardada_este_turno = True


def sumar_puntos(filas_eliminadas):
    global puntos, back_to_back, mostrar_back_to_back

    if filas_eliminadas == 0:
        mostrar_back_to_back = False
        return

    if filas_eliminadas == 1:
        puntos += 100
        mostrar_back_to_back = False
        back_to_back = False
    elif filas_eliminadas == 2:
        puntos += 300
        mostrar_back_to_back = False
        back_to_back = False
    elif filas_eliminadas == 3:
        puntos += 500
        mostrar_back_to_back = False
        back_to_back = False
    elif filas_eliminadas >= 4:
        base_puntos = 800
        if back_to_back:
            puntos += int(base_puntos * (1 + bonus_back_to_back))
            mostrar_back_to_back = True
        else:
            puntos += base_puntos
            mostrar_back_to_back = False
        back_to_back = True
    else:
        mostrar_back_to_back = False
        back_to_back = False

    actualizar_nivel()


def actualizar_nivel():
    global nivel, velocidad_caida, puntos_siguiente_nivel

    if puntos >= puntos_siguiente_nivel:
        nivel += 1
        velocidad_caida += 0.5
        puntos_siguiente_nivel += 1000


def dibujar_pieza_en_panel(forma, indice, pos_x, pos_y, tamano_bloque=20):
    for i, fila in enumerate(forma):
        for j, celda in enumerate(fila):
            if celda:
                x = pos_x + j * tamano_bloque
                y = pos_y + i * tamano_bloque
                pygame.draw.rect(pantalla, colores_piezas[indice], (x, y, tamano_bloque, tamano_bloque))
                pygame.draw.rect(pantalla, (0, 0, 0), (x, y, tamano_bloque, tamano_bloque), 1)


def colision_en(nueva_y):
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                ny = nueva_y + i
                nx = x_pieza + j

                if nx < 0 or nx >= COLUMNAS_TABLERO:
                    return True

                if ny >= FILAS:
                    return True

                if ny >= 0:
                    if tablero[ny][nx] is not None:
                        return True
    return False


def main():
    global x_pieza, y_pieza, tiempo_caida, tiempo_movimiento_horizontal, pausado

    running = True
    while running:
        pantalla.fill((0, 0, 0))
        crear_recuadro()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pausado = not pausado

        if pausado:
            fuente = pygame.font.SysFont(None, 50)
            texto_pausa = fuente.render("PAUSA", True, (255, 255, 255))
            pantalla.blit(texto_pausa, (ANCHO_PANTALLA // 2 - 60, ALTO_PANTALLA // 2 - 25))
            pygame.display.flip()
            clock.tick(60)
            continue

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - tiempo_caida > 1000 / velocidad_caida:
            if not colision_en(y_pieza + 1):
                y_pieza += 1
                tiempo_caida = tiempo_actual
            else:
                filas_eliminadas = colocar_pieza()
                sumar_puntos(filas_eliminadas)
                if not nueva_pieza():
                    fuente = pygame.font.SysFont(None, 60)
                    texto_game_over = fuente.render("GAME OVER", True, (255, 0, 0))
                    pantalla.blit(texto_game_over, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 30))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False

        keys = pygame.key.get_pressed()
        if tiempo_actual - tiempo_movimiento_horizontal > intervalo_movimiento:
            if keys[pygame.K_LEFT] and x_pieza > 0:
                x_pieza -= 1
                tiempo_movimiento_horizontal = tiempo_actual
                if colision():
                    x_pieza += 1

            if keys[pygame.K_RIGHT] and x_pieza < COLUMNAS_TABLERO - len(forma_pieza[0]):
                x_pieza += 1
                tiempo_movimiento_horizontal = tiempo_actual
                if colision():
                    x_pieza -= 1

        if keys[pygame.K_DOWN]:
            if not colision_en(y_pieza + 1):
                y_pieza += 1
            else:
                filas_eliminadas = colocar_pieza()
                sumar_puntos(filas_eliminadas)
                if not nueva_pieza():
                    fuente = pygame.font.SysFont(None, 60)
                    texto_game_over = fuente.render("GAME OVER", True, (255, 0, 0))
                    pantalla.blit(texto_game_over, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 30))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False

        if keys[pygame.K_SPACE]:
            if not espacio_presionado_anteriormente:
                while not colision_en(y_pieza + 1):
                    y_pieza += 1
                filas_eliminadas = colocar_pieza()
                sumar_puntos(filas_eliminadas)
                if not nueva_pieza():
                    fuente = pygame.font.SysFont(None, 60)
                    texto_game_over = fuente.render("GAME OVER", True, (255, 0, 0))
                    pantalla.blit(texto_game_over, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 30))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False
                tiempo_anterior = pygame.time.get_ticks()

            espacio_presionado_anteriormente = True
        else:
            espacio_presionado_anteriormente = False

        if keys[pygame.K_c]:
            guardar_pieza()

        if keys[pygame.K_UP]:
            rotar_pieza()

        for y in range(FILAS):
            for x in range(COLUMNAS_TABLERO):
                if tablero[y][x] is not None:
                    pygame.draw.rect(pantalla, colores_piezas[tablero[y][x]],
                                     (MARGEN_IZQUIERDO + x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, TAMANO_BLOQUE,
                                      TAMANO_BLOQUE))
                    pygame.draw.rect(pantalla, (0, 0, 0),
                                     (MARGEN_IZQUIERDO + x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, TAMANO_BLOQUE,
                                      TAMANO_BLOQUE), 1)

        crear_pieza()

        fuente = pygame.font.SysFont(None, 30)
        texto_puntos = fuente.render(f"Puntos: {puntos}", True, (255, 255, 255))
        pantalla.blit(texto_puntos, (10, 10))

        if mostrar_back_to_back:
            texto_b2b = fuente.render("Back-to-Back!", True, (255, 215, 0))
            pantalla.blit(texto_b2b, (10, 70))

        texto_nivel = fuente.render(f"Nivel: {nivel}", True, (0, 255, 0))
        pantalla.blit(texto_nivel, (10, 40))

        fuente_panel = pygame.font.SysFont(None, 24)
        texto_siguiente = fuente_panel.render("Siguiente:", True, (255, 255, 255))
        pantalla.blit(texto_siguiente, (ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 20))

        dibujar_pieza_en_panel(FORMAS[indice_pieza_siguiente], indice_pieza_siguiente,
                               ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 50)

        texto_guardada = fuente_panel.render("Guardada:", True, (255, 255, 255))
        pantalla.blit(texto_guardada, (ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 150))

        if pieza_guardada is not None:
            dibujar_pieza_en_panel(FORMAS[pieza_guardada], pieza_guardada, ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 180)

        pygame.display.flip()
        clock.tick(60)


main()
pygame.quit()