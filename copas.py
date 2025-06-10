import socket
import sys
import os
import time

import protocolo
import jogo
import player

#Local (por enquanto)
anel = (("127.0.0.1", 25259), 
        ("127.0.0.1", 25260), 
        ("127.0.0.1", 25261), 
        ("127.0.0.1", 25262))           

# testes de entrada
if len(sys.argv) != 2:
    print("Uso: python3 copas.py <id do player>")
    sys.exit(1)

pId = int(sys.argv[1])
eu = player.Player(pId, anel[(pId + 1)% 4], [])

if eu.pId not in range(4):
    print("Erro: Id invalida")
    print("Ids validas: 0, 1, 2, 3")
    sys.exit(1)

# configuração do anel
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
sock.bind(anel[eu.pId])
   
protocolo.conexao(sock, anel[(pId + 3)% 4], eu.pId, eu.prox)

# comeco do jogo
jogando = 1
cartasEmJogo = []

while jogando:
        
    if eu.bastao:
        if eu.estado == player.MESTRE:
            if not eu.joguei:
                if eu.pontos > jogo.PTOS_MAX:
                    jogo.fimDeJogo(sock, eu)
                    jogando = 0
                    espera = 0
                
                else:
                    if len(eu.cartas) == 0:
                        jogo.distribuiCartas(sock, eu)
                        print(f"Pontos: {eu.pontos}")
                        print("==============================================================================")
                        print("Suas cartas:")
                        jogo.imprimeCartas(eu.cartas, [1] * len(eu.cartas))
                    
                    jogo.jogada(sock, eu, cartasEmJogo)
                    eu.setJoguei()
        
                    protocolo.passaBastao(sock, eu, (eu.pId + 1) % 4)
                
            else:
                print("Cartas da rodada:")
                jogo.imprimeCartas(cartasEmJogo, [0] * 4)
            
                perde, pontos = jogo.fimRodada(sock, eu, cartasEmJogo)
                
                eu.resetJoguei()
                cartasEmJogo = []
                
                if perde != eu.pId:
                    print("Tranquilo! :)")
                    eu.setEstado(player.COMUM)
                    protocolo.passaBastao(sock, eu, perde)
                else:
                    print(f"+ {pontos} pontos :(")
                    
                print()
                print("=====================================")
                print() 
            
        elif eu.estado == player.COMUM:
            jogo.jogada(sock, eu, cartasEmJogo)
            eu.setJoguei()
            protocolo.passaBastao(sock, eu, (eu.pId + 1) % 4)
            

    else:
        msgVem = protocolo.esperaMsg(sock, eu.pId, eu.prox)
        
        if msgVem:
            if msgVem[protocolo.TIPO] == protocolo.DIST:
                print(f"Pontos: {eu.pontos}")
                print("==========================================================================")
                print("Suas cartas:")
                eu.setCartas(msgVem[protocolo.CART])
                jogo.imprimeCartas(eu.cartas, [1] * len(eu.cartas))
                
            elif msgVem[protocolo.TIPO] == protocolo.JOGA:
                cartasEmJogo = jogo.atualizaCartasEmJogo(msgVem)
                if not eu.joguei:
                    print("Cartas em jogo:")
                    jogo.imprimeCartas(cartasEmJogo, [0] * 4)
            
            elif msgVem[protocolo.TIPO] == protocolo.PTOS:
                
                cartasEmJogo = msgVem[protocolo.CART][0:4]
                perde = int(msgVem[protocolo.CART][4])
                
                pontos = int(msgVem[protocolo.CART][5])
                eu.atualizaPontos(pontos)
                
                print("Cartas da rodada:")
                jogo.imprimeCartas(cartasEmJogo, [0] * 4)
                
                cartasEmJogo = []
                eu.resetJoguei()
                
                if perde:
                    eu.setEstado(player.MESTRE)
                    print(f"+ {pontos} pontos :(")
                else:
                    print("Tranquilo! :)")
                
                print()
                print("=====================================")
                print()   
            
            elif msgVem[protocolo.TIPO] == protocolo.BAST:
                eu.bastao = 1
                
            elif msgVem[protocolo.TIPO] == protocolo.FIM:
                perde = msgVem[protocolo.ORIG]
                print(f"NÂO PERDEU com {eu.pontos} pontos! :D")
                print(f"PERDEDOR: {perde} com {msgVem[protocolo.CART][0]} pontos!")
                jogando = 0
                
                protocolo.mandaMsg(sock, eu.prox, perde, (eu.pId + 1) % 4, msgVem[protocolo.TIPO], msgVem[protocolo.CART])
                 
