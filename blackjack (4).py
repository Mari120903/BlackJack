import random
import numpy as np
import matplotlib.pyplot as plt
  
#1
#crea un mazo
def crear_mazo():
    #cartas = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    valores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    mazo = valores*4
    return mazo

#2
#crea un mazo total con la cantidad de mazos que se pidan
def crear_mazo_partida(n_barajas):
    mazo = crear_mazo()*n_barajas
    random.shuffle(mazo)
    return mazo
#3
#saca una carta
def tomar_carta(mazo):
    carta = mazo.pop(0)
    return carta

#4
#cuenta los as
def contar_as(mano):
    contador = 0
    i = 0
    while i < len(mano):
        if mano[i] == 1:
            contador += 1
        i += 1
    return contador

#cuenta los puntos
def contar_puntos(mano):
    i = 0
    cant_as = contar_as(mano)
    puntos = 0
    while i < len(mano):
        if mano[i] == 1 and puntos + 11 < 21 and cant_as == 1:
            puntos += 11
        else:
            puntos += mano[i]
        i += 1
    return puntos

#5
#devuelve true o false para seguir tomando cartas o no
def puede_tomar_carta(mano, limite):
    return contar_puntos (mano) < limite

#define el comportamiento del crupier
def crupier(mano, puntaje_jugador, mazo):
    mano_crupier = mano
    while contar_puntos(mano_crupier) < puntaje_jugador and puntaje_jugador <= 21 or contar_puntos(mano_crupier) < 17:
        mano_crupier.append(tomar_carta(mazo))
    return mano_crupier

#6
#juega una par6tida con un unico jugador
def jugar_partida (n_barajas, limite_jugador):
    mazo = crear_mazo_partida(n_barajas)    
    mano = []
    mano_crupier = []
    i = 0
    while i < 2:
        mano.append(tomar_carta(mazo))
        mano_crupier.append(tomar_carta(mazo))
        i += 1
    while contar_puntos(mano) < limite_jugador:
        mano.append(tomar_carta(mazo))
    mano_crupier= crupier(mano_crupier,contar_puntos(mano), mazo)
    return mano, mano_crupier

#7
#define si gano o perdio el casino devolviendo true o false
def casino_ganador(puntaje_final_jugador, puntaje_final_crupier):
    win = False
    if puntaje_final_crupier <= 21 and puntaje_final_crupier > puntaje_final_jugador or puntaje_final_jugador > 21:
        win = True
    return win

#verifica que haya empate
def empate(puntaje_final_jugador, puntaje_final_crupier):
    empate = False
    if puntaje_final_crupier <= 21 and puntaje_final_crupier == puntaje_final_jugador:
        empate = True
    return empate

#8
#actualiza el dinero dependiendo de cuanto se aposto y si se gano o no
def apuesta(n_barajas, limite_jugador, dinero_total, dinero_apostado):
    dinero = dinero_total
    mano_jugador, mano_crupier = jugar_partida(n_barajas, limite_jugador)
    if casino_ganador(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True and empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == False:
        dinero -= dinero_apostado
    elif casino_ganador(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == False and empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True:
        dinero += dinero_apostado
    elif empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True:
        dinero = dinero
    return dinero

#9
#simula un juego hata que el jugador se queda sin dinero 
def ruina_del_jugador(n_barajas, limite_jugador, dinero_total, dinero_apostado):
    dinero = dinero_total
    evolucion_dinero = [dinero_total]
    while dinero != 0:
        dinero = apuesta(n_barajas, limite_jugador, dinero, dinero_apostado)
        evolucion_dinero.append(dinero)
    return evolucion_dinero

#opcional
#simula una partida con varios jugadores
def jugar_partida_muchos_jugadores(n_barajas, m_jugadores, m_limites):
    mazo = crear_mazo_partida(n_barajas)
    manos = []
    for i in range(m_jugadores):
        manos.append([])
    mano_crupier = []
    i = 0
    jug_num = 0
    p = 0
    while i < 2:
        while jug_num < m_jugadores:
            manos[jug_num].append(tomar_carta(mazo))
            jug_num += 1
        mano_crupier.append(tomar_carta(mazo))
        i += 1
        p += 1
        jug_num = 0
    f = 0
    while contar_puntos(manos[f]) < m_limites[f]:
        if contar_puntos(manos[f]) < m_limites[f]:
            manos[f].append(tomar_carta(mazo))
        else:
            f += 1
    max_puntos_pos = 0
    max_puntos = 0
    contador = 0
    while contador < len(manos):
        if max_puntos < contar_puntos(manos[contador]):
            max_puntos_pos = contador
        contador += 1
    
    mano_crupier = crupier(mano_crupier,contar_puntos(manos[max_puntos_pos]), mazo)
    return manos, mano_crupier

#3.3
def crupier_tope(mano, puntaje_jugador, mazo, tope):
    mano_crupier = mano
    while contar_puntos(mano_crupier) < puntaje_jugador and contar_puntos(mano_crupier) < tope:
        mano_crupier.append(tomar_carta(mazo))
    return mano_crupier

def jugar_partida_con_tope(n_barajas, limite_jugador, tope):
    mazo = crear_mazo_partida(n_barajas)    
    mano = []
    mano_crupier = []
    i = 0
    while i < 2:
        mano.append(tomar_carta(mazo))
        mano_crupier.append(tomar_carta(mazo))
        i += 1
    while contar_puntos(mano) < limite_jugador:
        mano.append(tomar_carta(mazo))
    mano_crupier= crupier_tope(mano_crupier,contar_puntos(mano), mazo, tope)
    return mano, mano_crupier

def apuesta_tope(n_barajas, limite_jugador, dinero_total, dinero_apostado, tope):
    dinero = dinero_total
    mano_jugador, mano_crupier = jugar_partida_con_tope(n_barajas, limite_jugador, tope)
    if casino_ganador(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True and empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == False:
        dinero -= dinero_apostado
    elif casino_ganador(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == False and empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True:
        dinero += dinero_apostado
    elif empate(contar_puntos(mano_jugador), contar_puntos(mano_crupier)) == True:
        dinero = dinero
    return dinero

def ruina_del_jugador_tope(n_barajas, limite_jugador, dinero_total, dinero_apostado, tope):
    dinero = dinero_total
    evolucion_dinero = [dinero_total]
    while dinero != 0:
        dinero = apuesta_tope(n_barajas, limite_jugador, dinero, dinero_apostado, tope)
        evolucion_dinero.append(dinero)
    return evolucion_dinero
    
def dinamica_ganadora(lista):
    contador = 0
    i=0
    while i < len(lista)-1:
        if lista[i] < lista[i+1]:
            contador += 1
        i = i+1
    return contador / len (lista)

def simular_con_tope(cant_simulaciones, n_barajas, dinero_total, dinero_apostado, tope):
    lista = [[]]*cant_simulaciones
    promedios_sim = []
    for s in range(cant_simulaciones):
        promedios = []
        for l in range(1,22):
            lista[s]=ruina_del_jugador_tope(n_barajas, l, dinero_total, dinero_apostado, tope)
            promedios.append(dinamica_ganadora(lista[s]))
        promedios_sim.append(promedios)
    return promedios_sim

def promedio(lista):
    return sum(lista)/len(lista)

def grafico(cant_simulaciones, n_barajas, dinero_total, dinero_apostado, tope):
    resultados = simular_con_tope(cant_simulaciones, n_barajas, dinero_total, dinero_apostado, tope)
    promedios_sim=list (map(promedio, zip(*resultados)))
    plt.title("Probabilidad de ganarle al casino con limite (1-21)", color = "blue")
    plt.ylabel("Probabilidad")
    plt.xlabel("Limite puntos del jugador")
    return plt.plot(range(1,22), promedios_sim)