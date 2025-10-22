#!/usr/bin/env python3
"""
blackjack.py

Versión extendida del simulador de Blackjack con funciones adicionales:
- Double down (doblar apuesta en la primera decisión).
- Surrender (rendición temprana: recuperar mitad de la apuesta).
- Reshuffle automático cuando quedan pocas cartas en la "shoe".
- Estrategia de apuestas variable: fija o Martingale.
- Mantiene modo interactivo y modo de simulación (ruina del jugador).

Instrucciones: ejecutar python3 blackjack.py
"""
import random

# -------------------- Baraja y utilidades --------------------

def crear_mazo():
    """Devuelve una sola baraja (valores) sin palos."""
    valores = [1,2,3,4,5,6,7,8,9,10,10,10,10]
    return valores * 4


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

def contar_puntos(mano):
    total = 0
    aces = 0
    for c in mano:
        if c == 1:
            aces += 1
            total += 11
        else:
            total += c
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
    """
    Juega una mano usando el mazo provisto (se hace reshuffle si es necesario).
    - mazo: lista con cartas (se modifica por referencia).
    - n_barajas: usadas para rehacer la shoe cuando se necesita reshuffle.
    - limite_jugador: si automated=True, el jugador hará hit hasta este límite (estrategia simple).
    - allow_double / allow_surrender: habilita esas opciones.
    - automated: si False asume decisiones interactivas (no usado aquí; la interacción se maneja por separado).

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
    # Surrender: si permitido y jugador tiene 16 y crupier muestra 10 (heurística común)
    pj, _ = contar_puntos(jugador)
    upcard = crupier[0]
    if allow_surrender and automated:
        if pj == 16 and upcard == 10:
            # rendición temprana: se pierde la mitad de la apuesta
            return 'surrender', -0.5, jugador, crupier, mazo
    # Double: si permitido y total inicial 9-11 (heurística simple)
    doubled = False
    if allow_double and automated:
        if pj in (9, 10, 11):
            # doble: se dobla la apuesta, recibe una carta y se planta
            apuesta_factor = 2.0
            carta = tomar_carta(mazo)
            jugador.append(carta)
            doubled = True
            pj, _ = contar_puntos(jugador)
            # Si se pasa -> dealer gana
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
            # check bust early
            pj, _ = contar_puntos(jugador)
            if pj > 21:
                return 'dealer', -1 * apuesta_factor, jugador, crupier, mazo

    # Turno del crupier (si el jugador no se pasó)
    pj, _ = contar_puntos(jugador)
    # Si jugador ya se pasó, crupier no necesita jugar, pero mantendremos la mano para registro
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
    """
    Ejecuta una mano usando el mazo provisto y devuelve (nuevo_dinero, mazo, bet_used, resultado_codigo, jugador, crupier)
    betting_strategy: 'fixed' o 'martingale'
    last_bet: monto de la apuesta previa (para Martingale)
    """
    # Determinar apuesta a usar
    if betting_strategy == 'martingale' and last_bet is not None:
        # En Martingale, si la última apuesta fue una pérdida, la lógica de actualización la maneja el bucle
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
    # factor indica el multiplicador relativo de la apuesta (ej: 1 => gana 1*bet; -1 => pierde bet; 1.5 => blackjack)
    # Para surrender factor = -0.5
    if factor > 0:
        dinero += bet * factor
    elif factor < 0:
        dinero += bet * factor  # factor negativo representa pérdida (ej -1 => -bet; -0.5 => -0.5*bet)
    # push => factor == 0 => no cambio

    return dinero, mazo, bet, resultado, jugador, crupier


def ruina_del_jugador(n_barajas, limite_jugador, dinero_total, dinero_apostado,
                      max_rondas=10000, stand_on_soft17=True, allow_double=True,
                      allow_surrender=True, betting_strategy='fixed', reshuffle_threshold=15):
    """
    Simula rondas hasta que el jugador queda sin dinero o se alcanza max_rondas.
    Si betting_strategy == 'martingale' la apuesta se duplica tras cada pérdida (hasta el bankroll disponible).
    Devuelve evolución del dinero y algunas estadísticas.
    """
    mazo = crear_mazo_partida(n_barajas)
    dinero = dinero_total
    evolucion = [dinero]
    rondas = 0
    base_bet = dinero_apostado
    current_bet = base_bet

    while dinero > 0 and rondas < max_rondas:
        # evitar apostar más de lo que tenemos
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
        # Ajuste de Martingale: si perdió, doblar la apuesta la siguiente ronda; si ganó o push, reset
        if betting_strategy == 'martingale':
            # interpretamos pérdida si dinero decreased
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
    # Surrender
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