import random
import time
import os
import math

import protocolo
import player


PTOS_MAX = 100

# naipes
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



# se é possível traduzir pra int retorna 1
#                           c.c. retorna 0
def ehInt (isso):
    try:
        int(isso)
        return 1
    except ValueError:
        return 0

# retorna a naipe de uma carta
def naipe (carta):
    return math.floor(carta / 13)

# monta um vetor caracteristico composto xi = 1 caso a carta possa ser jogada
#                                           = 0 c.c.
def podeCartas (minhas, puxada):
    
    # checa se eh a primeira rodada
    if len(minhas) == 13:
        primeira = 1
    else:
        primeira = 0
    
    
    # caso nao tenha naipe puxada (primeira jogada da rodada)
    if puxada < 0:
        cartasPode = [1] * len(minhas)
        if (primeira):
            for i in range(len(minhas)):
                if (naipe(minhas[i]) == COPA | minhas[i] == MIQUE):
                    cartasPode[i] = 0
    
    cartasPode = [0] * len(minhas)
    
    # xi = 1 caso seja da naipe puxada
    for i in range(len(minhas)):
        if puxada == naipe(minhas[i]):
            if not primeira:
                cartasPode[i] = 1
            else:
                if minhas[i] != MIQUE:
                    cartasPode[i] = 1    
    
    # se nao eh possivel jogar nenhuma, pode jogal qualquer       
    if sum(cartasPode) == 0:
        for i in range(len(minhas)):
            if not primeira:
                cartasPode[i] = 1
            else:
                if (naipe(minhas[i]) != COPA) & (minhas[i] != MIQUE):
                    cartasPode[i] = 1 
    
    return cartasPode

# imprime cartas e indices com base no vetor caracteristico 
def imprimeCartas (minhas, cartasPode):

    for i in range(len(minhas)):
    
        carta = cartas[minhas[i]]
        
        # printa cor
        if (minhas[i] / 13) < 2:
            print(f"{VERM}", end="")
        else:
            print(f"{PRETO}", end="")
        
        print(f"%3s  {RESET}"% (carta), end=" ")
    
    print("")
    
    # printa indice das cartas que podem ser jogadas       
    for i in range(len(minhas)):
        if cartasPode[i]:
            print(f" %2d   "% (i), end="")
        else:
            print("      ", end="")
        
    print("")
            
    return    



# embaralha o deque
# manda mensagens p/ os outros com suas respectivas cartas
# atualiza as próprias cartas
def distribuiCartas (sock, eu):
    
    # embaralha
    random.shuffle(deque)
    
    for i in range(0,4):
        cartas = deque[i*13:(i*13)+13]
        if i != eu.pId:
            # manda 
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.DIST, cartas) 
        else:
            # atualiza
            eu.setCartas(cartas)       
    
    return

# imprime as cartas do jogador
# trata input
# manda msg
# atualiza cartas em jogo e cartas do jogador
def jogada (sock, eu, cartasEmJogo):
    print("Jogue uma carta: ")
    
    # se eh o primeiro a jogar na rodada, n tem naipe puxada
    if len(cartasEmJogo) > 0:
        puxada = naipe(cartasEmJogo[0])
    else:
        puxada = -1    
    
    # imprime
    cartasPode = podeCartas(eu.cartas, puxada)
    imprimeCartas(eu.cartas, cartasPode)
    
    # input
    inputBlz = 0
    while not inputBlz:
        carta = input()
        if (ehInt(carta)):
            carta = int(carta)
            if (0 <= carta < len(eu.cartas)):
                if (cartasPode[carta]):
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

# procedimentos de fim de rodada       
def fimRodada (sock, eu, cartasEmJogo):
    puxada = naipe(cartasEmJogo[0])
    
    # /  ----  /  -  /  -
    #  cartas  perde  ptos
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

# manda msg tipo FIM p/ todos   
def fimDeJogo (sock, eu):
    protocolo.mandaMsg(sock, eu.prox, eu.pId, (eu.pId + 1) % 4, protocolo.FIM, [eu.pontos])
    
    print(f"PERDEU :( com {eu.pontos} pontos")
    
