#!/usr/bin/env python3
"""
blackjack.py

Versión mejorada del simulador básico de Blackjack:
- Conteo correcto de Ases (1 u 11).
- Reglas del crupier (hit < 17; comportamiento en 17 suave configurable).
- Comparación de manos y pago de blackjack 3:2.
- Modo interactivo para jugar una mano en la consola.
- Modo de simulación (ruina del jugador).
"""
import random

def crear_mazo():
    valores = [1,2,3,4,5,6,7,8,9,10,10,10,10]  # A=1 (o 11), J/Q/K = 10
    return valores * 4

def crear_mazo_partida(n_barajas=1):
    mazo = crear_mazo() * n_barajas
    random.shuffle(mazo)
    return mazo

def tomar_carta(mazo):
    return mazo.pop()  # pop del final es O(1)

def contar_puntos(mano):
    """
    Devuelve (total, es_suave)
    es_suave = True si al menos un As cuenta como 11 en el total final.
    """
    total = 0
    aces = 0
    for c in mano:
        if c == 1:
            aces += 1
            total += 11
        else:
            total += c
    # Reducir Ases (11 -> 1) mientras total > 21
    reductions = 0
    aces_remaining = aces
    while total > 21 and aces_remaining > 0:
        total -= 10
        aces_remaining -= 1
        reductions += 1
    # Si hay al menos un As que sigue valiendo 11, es mano "suave"
    ace11_count = aces - reductions
    es_suave = ace11_count > 0
    return total, es_suave

def es_blackjack(mano):
    total, _ = contar_puntos(mano)
    return len(mano) == 2 and total == 21

def jugar_mano_basica(n_barajas, limite_jugador, stand_on_soft17=True):
    """
    Jugador sigue la estrategia simple: hit mientras puntos < limite_jugador.
    Devuelve (mano_jugador, mano_crupier).
    """
    mazo = crear_mazo_partida(n_barajas)
    jugador = [tomar_carta(mazo), tomar_carta(mazo)]
    crupier = [tomar_carta(mazo), tomar_carta(mazo)]

    # Jugador toma según límite
    while True:
        pj, _ = contar_puntos(jugador)
        if pj < limite_jugador:
            jugador.append(tomar_carta(mazo))
        else:
            break

    # Crupier juega: hit si total < 17; en 17 suave depende de stand_on_soft17
    while True:
        pc, es_suave_c = contar_puntos(crupier)
        if pc < 17:
            crupier.append(tomar_carta(mazo))
            continue
        if pc == 17 and es_suave_c and not stand_on_soft17:
            crupier.append(tomar_carta(mazo))
            continue
        break

    return jugador, crupier

def comparar_manos(jugador, crupier):
    """
    Devuelve (resultado, factor)
    resultado: 'player', 'dealer', 'push', 'player_blackjack'
    factor: multiplicador relativo del pago (1 = gana apuesta, -1 = pierde, 1.5 = blackjack)
    """
    pj, _ = contar_puntos(jugador)
    pc, _ = contar_puntos(crupier)
    j_black = es_blackjack(jugador)
    c_black = es_blackjack(crupier)

    if pj > 21:
        return 'dealer', -1
    if pc > 21:
        return 'player', 1
    if j_black and not c_black:
        return 'player_blackjack', 1.5
    if c_black and not j_black:
        return 'dealer', -1
    if pj > pc:
        return 'player', 1
    if pc > pj:
        return 'dealer', -1
    return 'push', 0

def apuesta(n_barajas, limite_jugador, dinero_total, dinero_apostado, stand_on_soft17=True):
    jugador, crupier = jugar_mano_basica(n_barajas, limite_jugador, stand_on_soft17)
    resultado, factor = comparar_manos(jugador, crupier)
    dinero = dinero_total
    if resultado == 'player_blackjack':
        dinero += dinero_apostado * 1.5
    elif resultado == 'player':
        dinero += dinero_apostado
    elif resultado == 'dealer':
        dinero -= dinero_apostado
    elif resultado == 'push':
        pass
    return dinero, resultado, jugador, crupier

def ruina_del_jugador(n_barajas, limite_jugador, dinero_total, dinero_apostado, max_rondas=10000, stand_on_soft17=True):
    dinero = dinero_total
    evolucion = [dinero]
    rondas = 0
    while dinero > 0 and rondas < max_rondas:
        dinero, resultado, _, _ = apuesta(n_barajas, limite_jugador, dinero, dinero_apostado, stand_on_soft17)
        evolucion.append(dinero)
        rondas += 1
    return evolucion

# ----- Modo interactivo -----
def mostrar_mano(mano):
    return "[" + ", ".join(str(c) for c in mano) + "]"

def jugar_interactivo(n_barajas=1, stand_on_soft17=True):
    mazo = crear_mazo_partida(n_barajas)
    jugador = [tomar_carta(mazo), tomar_carta(mazo)]
    crupier = [tomar_carta(mazo), tomar_carta(mazo)]
    print("Tus cartas:", mostrar_mano(jugador), "->", contar_puntos(jugador)[0])
    print("Carta visible del crupier:", crupier[0])
    # turno jugador
    while True:
        pj, _ = contar_puntos(jugador)
        if pj > 21:
            print("Te pasaste:", pj)
            break
        accion = input("¿Hit (h) o Stand (s)? ").strip().lower()
        if accion == 'h':
            carta = tomar_carta(mazo)
            jugador.append(carta)
            print("Tomas:", carta, "->", mostrar_mano(jugador), "=", contar_puntos(jugador)[0])
            continue
        elif accion == 's':
            break
        else:
            print("Entrada no válida. Escribe 'h' o 's'.")
    # turno crupier
    print("\nMano del crupier (revelada):", mostrar_mano(crupier), "->", contar_puntos(crupier)[0])
    while True:
        pc, es_suave = contar_puntos(crupier)
        pj_final, _ = contar_puntos(jugador)
        if pj_final > 21:
            print("Jugador ya bust, crupier se queda.")
            break
        if pc < 17:
            carta = tomar_carta(mazo)
            crupier.append(carta)
            print("Crupier toma:", carta, "->", mostrar_mano(crupier), "=", contar_puntos(crupier)[0])
            continue
        if pc == 17 and es_suave and not stand_on_soft17:
            carta = tomar_carta(mazo)
            crupier.append(carta)
            print("Crupier (17 suave) toma:", carta, "->", mostrar_mano(crupier), "=", contar_puntos(crupier)[0])
            continue
        break
    # resultado
    resultado, _ = comparar_manos(jugador, crupier)
    pj_final, _ = contar_puntos(jugador)
    pc_final, _ = contar_puntos(crupier)
    print("\nResultado final:")
    print("Jugador:", mostrar_mano(jugador), "=", pj_final)
    print("Crupier:", mostrar_mano(crupier), "=", pc_final)
    if resultado == 'player_blackjack':
        print("¡Jugador gana con Blackjack! (pago 3:2)")
    elif resultado == 'player':
        print("¡Jugador gana!")
    elif resultado == 'dealer':
        print("Crupier gana.")
    else:
        print("Empate (push).")
    return resultado

if __name__ == "__main__":
    random.seed()
    print("Blackjack simple - opciones:")
    print("1) Jugar interactivo (consola)")
    print("2) Simular ruina del jugador (estrategia límite 1-21)")
    opt = input("Elige 1 o 2: ").strip()
    if opt == '1':
        jugar_interactivo(n_barajas=1)
    else:
        # Ejemplo de simulación rápida
        print("Simulando ruina del jugador con límite 17, dinero inicial 100, apuesta 10...")
        ev = ruina_del_jugador(n_barajas=1, limite_jugador=17, dinero_total=100, dinero_apostado=10, max_rondas=1000)
        print("Evolución (primeras 20 entradas):", ev[:20])
        print("Número de rondas jugadas:", len(ev)-1)