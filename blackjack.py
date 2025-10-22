#!/usr/bin/env python3
"""
blackjack.py

Versión extendida del simulador de Blackjack usando representación de cartas como strings:
- Cartas: 'A','2'..'10','J','Q','K'
- Conteo correcto de Ases (1 u 11) en Hand
- Reglas: Double down, Surrender, Reshuffle automático y Martingale
- Modo interactivo y modo de simulación

Nota: este archivo será subido a la rama refactor/game-structure para refactor y PR.
"""
import random

# -------------------- Baraja y utilidades --------------------
CARD_RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def crear_mazo():
    """Devuelve una sola baraja como lista de strings (sin palos)."""
    return CARD_RANKS * 4

def crear_mazo_partida(n_barajas=1):
    mazo = crear_mazo() * n_barajas
    random.shuffle(mazo)
    return mazo

def ensure_mazo(mazo, n_barajas, threshold=15):
    """Reordena la shoe si quedan menos de 'threshold' cartas y devuelve el (posiblemente) nuevo mazo."""
    if mazo is None or len(mazo) < threshold:
        return crear_mazo_partida(n_barajas)
    return mazo

def tomar_carta(mazo):
    if not mazo:
        raise IndexError("El mazo está vacío. Asegúrate de reshuffle antes de tomar.")
    return mazo.pop()

# -------------------- Conteo de puntos --------------------
def valor_de_carta(card):
    """Mapea una carta string a su valor numérico (A como 1 aquí; 11 se maneja en contar_puntos)."""
    if card == 'A':
        return 1
    if card in ('J','Q','K'):
        return 10
    return int(card)

def contar_puntos(mano):
    """Devuelve (total, es_suave).
    Se cuentan los As como 11 inicialmente y se reducen a 1 mientras total > 21.
    """
    total = 0
    aces = 0
    for c in mano:
        if c == 'A':
            aces += 1
            total += 11
        else:
            total += valor_de_carta(c)
    reductions = 0
    aces_remaining = aces
    while total > 21 and aces_remaining > 0:
        total -= 10
        aces_remaining -= 1
        reductions += 1
    ace11_count = aces - reductions
    es_suave = ace11_count > 0
    return total, es_suave

def es_blackjack(mano):
    total, _ = contar_puntos(mano)
    return len(mano) == 2 and total == 21

# -------------------- Lógica de juego (una mano) --------------------
def jugar_mano_basica(mazo, n_barajas, limite_jugador, stand_on_soft17=True,
                      allow_double=True, allow_surrender=True, automated=True,
                      reshuffle_threshold=15):
    """Juega una mano usando el mazo provisto (se hace reshuffle si es necesario).

    Devuelve: (resultado_codigo, apuesta_multiplier, jugador_mano, crupier_mano, mazo)
    resultado_codigo: 'player','dealer','push','player_blackjack','surrender'
    apuesta_multiplier: factor que multiplica la apuesta original (por ejemplo: 1.5 para blackjack, -1 para perder, 0 para push, -0.5 para surrender)
    """
    # Asegurar mazo
    mazo = ensure_mazo(mazo, n_barajas, reshuffle_threshold)

    jugador = [tomar_carta(mazo), tomar_carta(mazo)]
    crupier = [tomar_carta(mazo), tomar_carta(mazo)]

    # Variables de la ronda
    apuesta_factor = 1.0  # cuánto vale la apuesta del jugador (1 = apuesta normal)

    # Chequear blackjack naturales tempranos
    if es_blackjack(jugador) or es_blackjack(crupier):
        # Si ambos blackjack -> push
        if es_blackjack(jugador) and es_blackjack(crupier):
            return 'push', 0, jugador, crupier, mazo
        if es_blackjack(jugador):
            return 'player_blackjack', 1.5, jugador, crupier, mazo
        return 'dealer', -1, jugador, crupier, mazo

    # Decisiones automáticas PRE-HIT (doble / surrender) basadas en heurística simple
    pj, _ = contar_puntos(jugador)
    upcard = crupier[0]
    if allow_surrender and automated:
        # Surrender heurística: si tiene 16 y la upcard es una carta de valor 10
        if pj == 16 and upcard in ('10','J','Q','K'):
            return 'surrender', -0.5, jugador, crupier, mazo
    # Double: si permitido y total inicial 9-11 (heurística simple)
    doubled = False
    if allow_double and automated:
        if pj in (9, 10, 11):
            apuesta_factor = 2.0
            carta = tomar_carta(mazo)
            jugador.append(carta)
            doubled = True
            pj, _ = contar_puntos(jugador)
            if pj > 21:
                return 'dealer', -1 * apuesta_factor, jugador, crupier, mazo
    # Si no se dobló, se aplica la política de hits simple (hit hasta limite)
    if not doubled:
        while True:
            pj, _ = contar_puntos(jugador)
            if pj < limite_jugador:
                jugador.append(tomar_carta(mazo))
            else:
                break
            pj, _ = contar_puntos(jugador)
            if pj > 21:
                return 'dealer', -1 * apuesta_factor, jugador, crupier, mazo

    # Turno del crupier
    pj, _ = contar_puntos(jugador)
    if pj <= 21:
        while True:
            pc, es_suave_c = contar_puntos(crupier)
            if pc < 17:
                crupier.append(tomar_carta(mazo))
                continue
            if pc == 17 and es_suave_c and not stand_on_soft17:
                crupier.append(tomar_carta(mazo))
                continue
            break

    # Comparar manos y devolver resultado con factor aplicado
    pj, _ = contar_puntos(jugador)
    pc, _ = contar_puntos(crupier)
    if pj > 21:
        return 'dealer', -1 * apuesta_factor, jugador, crupier, mazo
    if pc > 21:
        return 'player', 1 * apuesta_factor, jugador, crupier, mazo
    if pj > pc:
        return 'player', 1 * apuesta_factor, jugador, crupier, mazo
    if pc > pj:
        return 'dealer', -1 * apuesta_factor, jugador, crupier, mazo
    return 'push', 0, jugador, crupier, mazo

# -------------------- Apuesta y simulación --------------------
def apuesta_con_opciones(mazo, n_barajas, limite_jugador, dinero_total, dinero_apostado,
                          stand_on_soft17=True, allow_double=True, allow_surrender=True,
                          betting_strategy='fixed', last_bet=None, reshuffle_threshold=15):
    """Ejecuta una mano usando el mazo provisto y devuelve (nuevo_dinero, mazo, bet_used, resultado_codigo, jugador, crupier)"""
    if betting_strategy == 'martingale' and last_bet is not None:
        bet = last_bet
    else:
        bet = dinero_apostado

    resultado, factor, jugador, crupier, mazo = jugar_mano_basica(mazo, n_barajas, limite_jugador,
                                                                   stand_on_soft17=stand_on_soft17,
                                                                   allow_double=allow_double,
                                                                   allow_surrender=allow_surrender,
                                                                   automated=True,
                                                                   reshuffle_threshold=reshuffle_threshold)
    dinero = dinero_total
    if factor > 0:
        dinero += bet * factor
    elif factor < 0:
        dinero += bet * factor
    return dinero, mazo, bet, resultado, jugador, crupier

def ruina_del_jugador(n_barajas, limite_jugador, dinero_total, dinero_apostado,
                      max_rondas=10000, stand_on_soft17=True, allow_double=True,
                      allow_surrender=True, betting_strategy='fixed', reshuffle_threshold=15):
    """Simula rondas hasta que el jugador queda sin dinero o se alcanza max_rondas.
    Martingale: duplica la apuesta tras cada pérdida.
    """
    mazo = crear_mazo_partida(n_barajas)
    dinero = dinero_total
    evolucion = [dinero]
    rondas = 0
    base_bet = dinero_apostado
    current_bet = base_bet

    while dinero > 0 and rondas < max_rondas:
        if current_bet > dinero:
            current_bet = dinero
        dinero_antes = dinero
        dinero, mazo, bet_used, resultado, jugador, crupier = apuesta_con_opciones(
            mazo, n_barajas, limite_jugador, dinero, current_bet,
            stand_on_soft17=stand_on_soft17, allow_double=allow_double,
            allow_surrender=allow_surrender, betting_strategy=betting_strategy,
            last_bet=current_bet, reshuffle_threshold=reshuffle_threshold)
        evolucion.append(dinero)
        rondas += 1
        if betting_strategy == 'martingale':
            if dinero < dinero_antes:
                current_bet = min(current_bet * 2, dinero)
            else:
                current_bet = base_bet
    return evolucion

# -------------------- Modo interactivo (con doble y surrender) --------------------
def mostrar_mano(mano):
    return "[" + ", ".join(str(c) for c in mano) + "]"

def jugar_interactivo(n_barajas=1, stand_on_soft17=True, allow_double=True, allow_surrender=True,
                      reshuffle_threshold=15):
    mazo = crear_mazo_partida(n_barajas)
    mazo = ensure_mazo(mazo, n_barajas, reshuffle_threshold)
    jugador = [tomar_carta(mazo), tomar_carta(mazo)]
    crupier = [tomar_carta(mazo), tomar_carta(mazo)]

    print("Tus cartas:", mostrar_mano(jugador), "->", contar_puntos(jugador)[0])
    print("Carta visible del crupier:", crupier[0])

    # Preguntar por surrender o double antes de tomar hits
    if allow_surrender:
        respuesta = input("¿Quieres rendirte y recuperar la mitad de la apuesta? (s/n) ").strip().lower()
        if respuesta == 's':
            print("Te rendiste. Pierdes la mitad de tu apuesta.")
            return 'surrender', jugador, crupier
    # Double
    doubled = False
    if allow_double:
        respuesta = input("¿Quieres doblar la apuesta (double down) ahora? (s/n) ").strip().lower()
        if respuesta == 's':
            doubled = True
            carta = tomar_carta(mazo)
            jugador.append(carta)
            print("Has doblado y recibiste:", carta, "->", mostrar_mano(jugador), "=", contar_puntos(jugador)[0])
    # Si no se dobló, permitir hits hasta stand
    if not doubled:
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

    # Turno del crupier
    print("\nMano del crupier (revelada):", mostrar_mano(crupier), "->", contar_puntos(crupier)[0])
    pj_final, _ = contar_puntos(jugador)
    while pj_final <= 21:
        pc, es_suave = contar_puntos(crupier)
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

    # Resultado
    resultado, factor = comparar_manos_interactivo(jugador, crupier)
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
    elif resultado == 'surrender':
        print("Jugador se rindió. Pierde la mitad de la apuesta.")
    else:
        print("Empate (push).")
    return resultado

def comparar_manos_interactivo(jugador, crupier):
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

# -------------------- Función principal y ayuda --------------------
if __name__ == "__main__":
    random.seed()
    print("Blackjack extendido - opciones:")
    print("1) Jugar interactivo (con doble y surrender)")
    print("2) Simular ruina del jugador (con Martingale opcional)")
    opt = input("Elige 1 o 2: ").strip()
    if opt == '1':
        jugar_interactivo(n_barajas=1)
    else:
        print("Parámetros de la simulación:")
        n_bar = int(input("Cantidad de barajas (ej 1): ").strip() or 1)
        limite = int(input("Límite del jugador (hit hasta): ").strip() or 17)
        dinero = float(input("Dinero inicial (ej 100): ").strip() or 100)
        apuesta = float(input("Apuesta base (ej 10): ").strip() or 10)
        strat = input("Estrategia de apuesta ('fixed' o 'martingale'): ").strip() or 'fixed'
        ev = ruina_del_jugador(n_bar, limite, dinero, apuesta, max_rondas=1000,
                               betting_strategy=strat)
        print("Evolución (primeras 30 entradas):", ev[:30])
