import random
import time
import os
import math

import protocolo
import player


PTOS_MAX = 100

OURO = 0
COPA = 1 
SPDA = 2
PAUS = 3

# cores p/ print
PRETO = "\033[38;2;0;0;0;48;2;255;255;255m"
VERM  = "\033[38;2;255;0;0;48;2;255;255;255m"
RESET = "\033[0m"

cartas = ["2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦", "A♦", 
          "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥", "A♥", 
          "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠", "A♠", 
          "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣", "A♣"]

MIQUE = 36

deque = list(range(52))

def ehInt (isso):
    try:
        int(isso)
        return 1
    except ValueError:
        return 0

def naipe (carta):
    return math.floor(carta / 13)

def naipeCerta (minhas, puxada):
    
    if len(minhas) == 13:
        primeira = 1
    else:
        primeira = 0
    
    if puxada < 0:
        cartasNaipe = [1] * len(minhas)
        if (primeira):
            for i in range(len(minhas)):
                if (naipe(minhas[i]) == COPA | minhas[i] == MIQUE):
                    cartasNaipe[i] = 0
    
    cartasNaipe = [0] * len(minhas)
   
    for i in range(len(minhas)):
        if puxada == naipe(minhas[i]):
            if not primeira:
                cartasNaipe[i] = 1
            else:
                if (naipe(minhas[i]) != COPA) & (minhas[i] != MIQUE):
                    cartasNaipe[i] = 1    
            
    if sum(cartasNaipe) == 0:
        for i in range(len(minhas)):
            if not primeira:
                cartasNaipe[i] = 1
            else:
                if (naipe(minhas[i]) != COPA) & (minhas[i] != MIQUE):
                    cartasNaipe[i] = 1 
    
    return cartasNaipe

def imprimeCartas (minhas, cartasNaipe):

    for i in range(len(minhas)):
    
        carta = cartas[minhas[i]]
        
        if (minhas[i] / 13) < 2:
            print(f"{VERM}", end="")
        else:
            print(f"{PRETO}", end="")
        
        print(f"%3s  {RESET}"% (carta), end=" ")
    
    print("")
            
    for i in range(len(minhas)):
        if cartasNaipe[i]:
            print(f" %2d   "% (i), end="")
        else:
            print("      ", end="")
        
    print("")
            
    return naipeCerta   

def distribuiCartas (sock, eu):
    
    random.shuffle(deque)
    
    for i in range(0,4):
        cartas = deque[i*13:(i*13)+13]
        if i != eu.pId:
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.DIST, cartas) 
        else:
            eu.setCartas(cartas)       
    
    return
      
def jogada (sock, eu, cartasEmJogo):
    print("Jogue uma carta: ")
    
    if len(cartasEmJogo) > 0:
        puxada = naipe(cartasEmJogo[0])
    else:
        puxada = -1    
    
    cartasNaipe = naipeCerta(eu.cartas, puxada)
    
    imprimeCartas(eu.cartas, cartasNaipe)
    
    inputBlz = 0
    while not inputBlz:
        carta = input()
        if (ehInt(carta)):
            carta = int(carta)
            if (0 <= carta < len(eu.cartas)):
                if (cartasNaipe[carta]):
                    inputBlz = 1
                else:
                    print("Escolha uma das cartas da naipe puxada.")
            else:
                print("Por favor insira um número entre 0 e %d"% (len(eu.cartas)))
        else:
            print("Por favor insira um número")
    
    cartasEmJogo.append(eu.cartas[carta])
    protocolo.mandaMsg(sock, eu.prox, eu.pId, (eu.pId + 1) % 4, protocolo.JOGA, cartasEmJogo)
    eu.cartas.remove(eu.cartas[carta])
    
    return cartasEmJogo

def atualizaCartasEmJogo (msgVem):
    cartasEmJogo = msgVem[protocolo.CART][0:4]
            
    numCartas = 4
    for i in range(3, -1, -1):
        if cartasEmJogo[i] == 52:
            numCartas = i
            
    return cartasEmJogo[0:numCartas]
       
def fimRodada (sock, eu, cartasEmJogo):
    puxada = naipe(cartasEmJogo[0])
    
    info = [0] * 6
    
    # calcula pontos e perdedor
    pontos = 0
    perdedor = 0
    for i in range(0,4):
        info[i] = cartasEmJogo[i]
    
        if (naipe(cartasEmJogo[i]) == puxada) & (cartasEmJogo[i] > cartasEmJogo[perdedor]): 
            perdedor = i
            
        if naipe(cartasEmJogo[i]) == COPA:
            pontos += 1
        elif cartasEmJogo[i] == MIQUE:
            pontos += 13
    
    perdedor = (eu.pId + perdedor) % 4
    
    # manda mesagem com os pontos p/ o perdedor e com 0 p/ os outros        
    for i in range(4):
        if i == eu.pId:  
            if perdedor == eu.pId:
                eu.atualizaPontos(pontos)
        elif i == perdedor:
            info[4] = 1
            info[5] = pontos
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.PTOS, info)
            info[4] = 0
            info[5] = 0
        else:
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.PTOS, info)
                
                
    return perdedor, pontos
    
def fimDeJogo (sock, eu):
    protocolo.mandaMsg(sock, eu.prox, eu.pId, (eu.pId + 1) % 4, protocolo.FIM, [eu.pontos])
    
    print(f"PERDEU :( com {eu.pontos} pontos")
    
