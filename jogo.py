import random
import time
import os
import math

import protocolo
import player

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
    
    if puxada < 0:
        return [1] * len(minhas)
    
    cartasNaipe = [0] * len(minhas)
   
    for i in range(len(minhas)):
        if puxada == naipe(minhas[i]):
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
    
def esperaCartas (sock, eu):

    while 1:
        msgVem = protocolo.esperaMsg(sock, eu.pId, eu.prox)
        if msgVem:
            if msgVem[protocolo.TIPO] == protocolo.DIST:
                eu.cartas = msgVem[protocolo.CART]
                return (1, 0)
                
            elif msgVem[protocolo.TIPO] == protocolo.FIM:
                print("GANHOU com {eu.pontos} pontos! :D")
                print("PERDEDOR: {msgVem[protocolo.ORIG]} com {msgVem[protocolo.CART[0]]} pontos!")
                return (0, 1)
                  
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
    
    eu.joguei = 1
    
    protocolo.passaBastao(sock, eu, (eu.pId + 1) % 4)
    
    return cartasEmJogo
    
def esperaJogada (sock, eu):
    msgVem = protocolo.esperaMsg(sock, eu.pId, eu.prox)
    
    if msgVem:
        if msgVem[protocolo.TIPO] == protocolo.JOGA: 
            cartasEmJogo = msgVem[protocolo.CART][0:4]
            
            numCartas = 4
            for i in range(3, -1, -1):
                if cartasEmJogo[i] == 52:
                    numCartas = i
                    
            return 0, 0, cartasEmJogo[0:numCartas]
            
        elif msgVem[protocolo.TIPO] == protocolo.BAST:
            return 1, 0, 0
            
        elif msgVem[protocolo.TIPO] == protocolo.PTOS:
            if int(msgVem[protocolo.CART][0]) > 0:
                eu.pontos += int(msgVem[protocolo.CART][0])
                
                while 1:
                    msgVem = protocolo.esperaMsg(sock, eu, eu.prox)
                    if msgVem: 
                        if msgVem[protocolo.TIPO] == protocolo.BAST:
                            return 1, 1, 0
                    
            return 0, 1, 0
        
    return 0, 0, 0
        
def fimJogada (sock, eu, cartasEmJogo):
    puxada = naipe(cartasEmJogo[0])
    
    pontos = 0
    maior = 0
    for i in range(1,4):
        if (naipe(cartasEmJogo[i]) == puxada) & (cartasEmJogo[i] > cartasEmJogo[maior]): 
            maior = i
            
        if naipe(cartasEmJogo[i]) == COPA:
            pontos += 1
        elif cartasEmJogo[i] == MIQUE:
            pontos += 13
            
    for i in range(4):
        if i != eu.pId:  
            if (eu.pId + maior) % 4 == i:  
                protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.PTOS, [pontos])
            else:
                protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.PTOS, [0])
            
        else:
            if maior == 0:
                eu.pontos += pontos
                return 1
          
    protocolo.passaBastao(sock, eu, (eu.pId + maior) % 4)
                
    return 0
    
def fimDeJogo (sock, eu):
    for i in range(4):
        if i != eu.pId:
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.FIM, [eu.pontos])
    
    print("PERDEU :( com {eu.pontos} pontos")
    
