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
#constantes
COLUMNAS = 10
FILAS = 20
TAM_BLOQUE = 30
#Dimensiones que tiene el tablero

ANCHO_TABLERO = COLUMNAS * TAM_BLOQUE  # 300 px
ALTO_PANTALLA = FILAS * TAM_BLOQUE  # 600 px
ESPACIO_LATERAL = 150
MARGEN_IZQUIERDO = 200
ANCHO_PANTALLA = MARGEN_IZQUIERDO + ANCHO_TABLERO + ESPACIO_LATERAL
#Pantalla

ARCHIVO_RECORDS= "records.txt"
MAX_RECORDS = 10
#Records


#variables
tablero = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]

indice_pieza_actual = random.randint(0, len(FORMAS) - 1)
forma_pieza = FORMAS[indice_pieza_actual]
x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
y_pieza = 0

velocidad_caida = 1.5
tiempo_caida = pygame.time.get_ticks()

tiempo_movimiento_horizontal = pygame.time.get_ticks()
intervalo_movimiento = 200
tiempo_ultima_rotacion = 0
delay_rotacion = 200

espacio_presionado_anteriormente = False
pieza_guardada = None
pieza_guardada_anteriormente = False

pausado = False
puntos = 0
back_to_back = False
bonus_back_to_back = 0.5
nivel = 1
puntos_siguiente_nivel = 1000

indice_pieza_siguiente = random.randint(0, len(FORMAS) - 1)
mostrar_back_to_back = False

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris")
def cargar_records():
    records = []
    try:
        with open("records.txt", "r") as f:
            for linea in f:
                partes = linea.strip().split(",")
                if len(partes) == 2:
                    nombre, puntaje = partes[0], int(partes[1])
                    records.append((nombre, puntaje))
    except FileNotFoundError:
        pass
    return records


def guardar_records(records):
    with open("records.txt", "w") as f:
        for nombre, puntaje in records[:10]:
            f.write(f"{nombre},{puntaje}\n")


def agregar_nuevo_record(nombre, puntaje):
    records = cargar_records()
    records.append((nombre, puntaje))
    records.sort(key=lambda x: x[1], reverse=True)
    guardar_records(records)


def entra_en_top(puntuacion):
    records = cargar_records()
    if len(records) < 10:
        return True
    return puntuacion > records[-1][1]










def crear_pieza():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                x = MARGEN_IZQUIERDO + (x_pieza + j) * TAM_BLOQUE
                y = (y_pieza + i) * TAM_BLOQUE
                pygame.draw.rect(pantalla, colores_piezas[indice_pieza_actual], (x, y, TAM_BLOQUE, TAM_BLOQUE))
                pygame.draw.rect(pantalla, (0, 0, 0), (x, y, TAM_BLOQUE, TAM_BLOQUE), 1)


def crear_recuadro():
    for x in range(0, ANCHO_TABLERO + 1, TAM_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (x + MARGEN_IZQUIERDO, 0), (x + MARGEN_IZQUIERDO, ALTO_PANTALLA))
    for y in range(0, ALTO_PANTALLA + 1, TAM_BLOQUE):
        pygame.draw.line(pantalla, (50, 50, 70), (MARGEN_IZQUIERDO, y), (MARGEN_IZQUIERDO + ANCHO_TABLERO, y))


def colision():
    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                ny = y_pieza + i
                nx = x_pieza + j
                if nx < 0 or nx >= COLUMNAS:
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
    global forma_pieza, x_pieza, y_pieza, indice_pieza_actual, pieza_guardada_anteriormente, indice_pieza_siguiente

    indice_pieza_actual = indice_pieza_siguiente
    forma_pieza = FORMAS[indice_pieza_actual]
    x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
    y_pieza = 0
    pieza_guardada_anteriormente = False

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
        for x in range(COLUMNAS):
            if tablero[y][x] is None:
                linea_completa = False
                break
        if linea_completa:
            eliminadas += 1
            for y2 in range(y, 0, -1):
                tablero[y2] = tablero[y2 - 1].copy()
            tablero[0] = [None] * COLUMNAS
            y += 1
        y -= 1
    return eliminadas


def guardar_pieza():
    global pieza_guardada, forma_pieza, indice_pieza_actual, x_pieza, y_pieza, pieza_guardada_anteriormente

    if pieza_guardada_anteriormente:
        return

    if pieza_guardada is None:
        pieza_guardada = indice_pieza_actual
        if not nueva_pieza():
            pygame.quit()
            exit()
    else:
        pieza_guardada, indice_pieza_actual = indice_pieza_actual, pieza_guardada
        forma_pieza = FORMAS[indice_pieza_actual]
        x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
        y_pieza = 0
        if colision():
            pygame.quit()
            exit()

    pieza_guardada_anteriormente = True


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

                if nx < 0 or nx >= COLUMNAS:
                    return True

                if ny >= FILAS:
                    return True

                if ny >= 0:
                    if tablero[ny][nx] is not None:
                        return True
    return False


def dibujar_ghost_piece():
    ghost_y = y_pieza
    while not colision_en(ghost_y + 1):
        ghost_y += 1

    for i, fila in enumerate(forma_pieza):
        for j, celda in enumerate(fila):
            if celda:
                x = MARGEN_IZQUIERDO + (x_pieza + j) * TAM_BLOQUE
                y = (ghost_y + i) * TAM_BLOQUE
                color = colores_piezas[indice_pieza_actual]
                color_translucido = (color[0] // 3, color[1] // 3, color[2] // 3)
                pygame.draw.rect(pantalla, color_translucido, (x, y, TAM_BLOQUE, TAM_BLOQUE))
                pygame.draw.rect(pantalla, (50, 50, 50), (x, y, TAM_BLOQUE, TAM_BLOQUE), 1)


def menu_pausa():
    opciones = ["Reanudar", "Reiniciar", "Salir"]
    opcion_seleccionada = 0
    fuente = pygame.font.SysFont(None, 40)
    fuente_titulo = pygame.font.SysFont(None, 60)

    while True:
        pantalla.fill((20, 20, 20))

        texto_titulo = fuente_titulo.render("PAUSA", True, (255, 255, 255))
        pantalla.blit(texto_titulo, (
            ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2,
            ALTO_PANTALLA // 4 - texto_titulo.get_height() // 2
        ))

        for i, texto in enumerate(opciones):
            es_seleccionada = i == opcion_seleccionada
            color = (255, 255, 0) if es_seleccionada else (255, 255, 255)
            prefijo = "> " if es_seleccionada else " "
            render = fuente.render(prefijo + texto, True, color)
            x = ANCHO_PANTALLA // 2 - render.get_width() // 2
            y = ALTO_PANTALLA // 2 + i * 50
            pantalla.blit(render, (x, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                elif event.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
                elif event.key == pygame.K_RETURN:
                    return opciones[opcion_seleccionada].lower()


def reiniciar_juego():
    global tablero, indice_pieza_actual, forma_pieza, x_pieza, y_pieza
    global velocidad_caida, tiempo_caida, tiempo_movimiento_horizontal
    global pieza_guardada, pieza_guardada_anteriormente, pausado
    global puntos, back_to_back, nivel, puntos_siguiente_nivel
    global indice_pieza_siguiente, mostrar_back_to_back

    tablero = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
    indice_pieza_actual = random.randint(0, len(FORMAS) - 1)
    forma_pieza = FORMAS[indice_pieza_actual]
    x_pieza = COLUMNAS // 2 - len(forma_pieza[0]) // 2
    y_pieza = 0
    velocidad_caida = 1.0
    tiempo_caida = pygame.time.get_ticks()
    tiempo_movimiento_horizontal = pygame.time.get_ticks()
    pieza_guardada = None
    pieza_guardada_anteriormente = False
    pausado = False
    puntos = 0
    back_to_back = False
    nivel = 1
    puntos_siguiente_nivel = 1000
    indice_pieza_siguiente = random.randint(0, len(FORMAS) - 1)
    mostrar_back_to_back = False


def ingresar_nombre():
    letras = [chr(i) for i in range(65, 91)]
    seleccion = [0, 0, 0]
    posicion = 0
    fuente = pygame.font.SysFont(None, 50)

    while True:
        pantalla.fill((0, 0, 0))

        # Texto
        titulo = fuente.render("¡Nuevo récord!", True, (255, 255, 255))
        pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 100))

        instruccion = pygame.font.SysFont(None, 30).render(
            "Usa flechas para escribir tus 3 letras y Enter para confirmar", True, (200, 200, 200))
        pantalla.blit(instruccion, (ANCHO_PANTALLA // 2 - instruccion.get_width() // 2, 150))

        for i in range(3):
            letra = letras[seleccion[i]]
            color = (255, 255, 0) if i == posicion else (255, 255, 255)
            texto = fuente.render(letra, True, color)
            pantalla.blit(texto, (
                ANCHO_PANTALLA // 2 - 60 + i * 40,
                ALTO_PANTALLA // 2
            ))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "AAA"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    posicion = (posicion - 1) % 3
                elif event.key == pygame.K_RIGHT:
                    posicion = (posicion + 1) % 3
                elif event.key == pygame.K_UP:
                    seleccion[posicion] = (seleccion[posicion] - 1) % len(letras)
                elif event.key == pygame.K_DOWN:
                    seleccion[posicion] = (seleccion[posicion] + 1) % len(letras)
                elif event.key == pygame.K_RETURN:
                    nombre = "".join([letras[i] for i in seleccion])
                    return nombre


def menu_principal():
    opciones = ["Jugar", "Hall of Fame", "Salir"]
    opcion_seleccionada = 0
    fuente = pygame.font.SysFont(None, 40)
    fuente_titulo = pygame.font.SysFont(None, 60)

    while True:
        pantalla.fill((10, 10, 30))

        texto_titulo = fuente_titulo.render("TETRIS", True, (255, 255, 255))
        pantalla.blit(texto_titulo, (
            ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2,
            ALTO_PANTALLA // 4
        ))

        for i, texto in enumerate(opciones):
            es_seleccionada = i == opcion_seleccionada
            color = (255, 255, 0) if es_seleccionada else (255, 255, 255)
            prefijo = "> " if es_seleccionada else "  "
            render = fuente.render(prefijo + texto, True, color)
            pantalla.blit(render, (
                ANCHO_PANTALLA // 2 - render.get_width() // 2,
                ALTO_PANTALLA // 2 + i * 50
            ))

        fuente_version = pygame.font.SysFont(None, 20)
        texto_version = fuente_version.render("Ver 1.0", True, (180, 180, 180))
        pantalla.blit(texto_version, (10, ALTO_PANTALLA - 25))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                elif event.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
                elif event.key == pygame.K_RETURN:
                    return opciones[opcion_seleccionada].lower()


def mostrar_hall_of_fame():
    fuente_titulo = pygame.font.SysFont(None, 50)
    fuente = pygame.font.SysFont(None, 30)

    records = cargar_records()

    while True:
        pantalla.fill((10, 10, 30))
        titulo = fuente_titulo.render("Hall of Fame", True, (255, 255, 255))
        pantalla.blit(titulo, (ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 50))

        for i, (nombre, puntaje) in enumerate(records[:10]):
            texto = fuente.render(f"{i + 1}. {nombre} - {puntaje}", True, (200, 200, 200))
            pantalla.blit(texto, (ANCHO_PANTALLA // 2 - 100, 120 + i * 30))

        instruccion = fuente.render("Presiona ESC para volver", True, (150, 150, 150))
        pantalla.blit(instruccion, (ANCHO_PANTALLA // 2 - instruccion.get_width() // 2, ALTO_PANTALLA - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "volver"


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
            accion = menu_pausa()
            if accion == "reanudar":
                pausado = False
            elif accion == "reiniciar":
                reiniciar_juego()
            elif accion == "salir":
                return "menu"
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
                    if entra_en_top(puntos):
                        nombre = ingresar_nombre()
                        agregar_nuevo_record(nombre, puntos)
                    running = False

        keys = pygame.key.get_pressed()
        if tiempo_actual - tiempo_movimiento_horizontal > intervalo_movimiento:
            if keys[pygame.K_LEFT] and x_pieza > 0:
                x_pieza -= 1
                tiempo_movimiento_horizontal = tiempo_actual
                if colision():
                    x_pieza += 1

            if keys[pygame.K_RIGHT] and x_pieza < COLUMNAS - len(forma_pieza[0]):
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
            for x in range(COLUMNAS):
                if tablero[y][x] is not None:
                    pygame.draw.rect(pantalla, colores_piezas[tablero[y][x]],
                                     (MARGEN_IZQUIERDO + x * TAM_BLOQUE, y * TAM_BLOQUE, TAM_BLOQUE,
                                      TAM_BLOQUE))
                    pygame.draw.rect(pantalla, (0, 0, 0),
                                     (MARGEN_IZQUIERDO + x * TAM_BLOQUE, y * TAM_BLOQUE, TAM_BLOQUE,
                                      TAM_BLOQUE), 1)

        dibujar_ghost_piece()

        crear_pieza()

        fuente = pygame.font.SysFont(None, 30)
        texto_puntos = fuente.render(f"Puntos: {puntos}", True, (255, 255, 255))
        pantalla.blit(texto_puntos, (10, 10))

        if mostrar_back_to_back:
            texto_b2b = fuente.render("Back-to-Back!", True, (255, 215, 0))
            pantalla.blit(texto_b2b, (10, 70))

        texto_nivel = fuente.render(f"Nivel: {nivel}", True, (0, 255, 0))
        pantalla.blit(texto_nivel, (10, 40))

        records = cargar_records()
        fuente = pygame.font.SysFont(None, 24)
        pantalla.blit(fuente.render("Top 3:", True, (255, 255, 255)), (10, 100))
        for i, (nombre, score) in enumerate(records[:3]):
            texto = fuente.render(f"{i + 1}. {nombre} - {score}", True, (200, 200, 200))
            pantalla.blit(texto, (10, 130 + i * 30))

        fuente_panel = pygame.font.SysFont(None, 24)
        texto_siguiente = fuente_panel.render("Siguiente:", True, (255, 255, 255))
        pantalla.blit(texto_siguiente, (ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 20))

        dibujar_pieza_en_panel(FORMAS[indice_pieza_siguiente], indice_pieza_siguiente,
                               ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 50)

        texto_guardado = fuente_panel.render("Guardada:", True, (255, 255, 255))
        pantalla.blit(texto_guardado, (ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 150))

        if pieza_guardada is not None:
            dibujar_pieza_en_panel(FORMAS[pieza_guardada], pieza_guardada, ANCHO_PANTALLA - ESPACIO_LATERAL + 20, 180)

        pygame.display.flip()
        clock.tick(60)


while True:
    opcion = menu_principal()
    if opcion == "jugar":
        reiniciar_juego()
        resultado = main()
        if resultado == "menu":
            continue
        elif resultado == "reiniciar":
            continue
    elif opcion == "hall of fame":
        resultado = mostrar_hall_of_fame()
        if resultado == "salir":
            break
    elif opcion == "salir":
        break

pygame.quit()