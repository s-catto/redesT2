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
rodada = 1

while jogando:

    if eu.bastao:
        jogo.distribuiCartas(sock, eu)
        print("foi")
        jogo.imprimeCartas(eu.cartas)

    else:
        jogo.esperaCartas(sock, eu)
        print("chegou")
        jogo.imprimeCartas(eu.cartas)
        
    while rodada:
        protocolo.esperaMsg(sock, eu.pId, eu.prox)
            
            #if eu.bastao:
            #    jogo.jogada()
            #    eu.passaBastao()
