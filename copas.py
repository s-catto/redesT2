import socket
import sys
import os

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
fimRodada = 0
cartasEmJogo = []

while jogando:
    eu.joguei = 0
    cartasEmJogo = []
        
    if eu.bastao:
        jogo.distribuiCartas(sock, eu)
        jogo.imprimeCartas(eu.cartas, [1] * len(eu.cartas))

    else:
        jogando, fimRodada = jogo.esperaCartas(sock, eu)
        jogo.imprimeCartas(eu.cartas, [1] * len(eu.cartas))
    
    while not fimRodada:    
        if eu.bastao == 1:
            if not eu.joguei:
                cartasEmJogo = jogo.jogada(sock, eu, cartasEmJogo)
            else:
                perdi = jogo.fimJogada(sock, eu, cartasEmJogo)
                fimRodada = 1
                if perdi:
                    if eu.pontos >= 100:
                        jogando = 0
                        jogo.fimDeJogo(sock, eu)
        else:
            eu.bastao, fimRodada, cartas = jogo.esperaJogada(sock, eu)
            if (cartas):
                cartasEmJogo = cartas
                print("Cartas em jogo:")
                jogo.imprimeCartas(cartasEmJogo, [0] * len(cartasEmJogo))
                
            if eu.pontos >= 100:
                jogando = 0
                jogo.fimDeJogo(sock, eu)    

    if eu.bastao:
        print("Perdeu a rodada :(")
        print("Pontos: {eu.pontos}")
    else:
        print("Ufa! Não perdeu a rodada!")               
