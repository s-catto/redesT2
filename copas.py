import socket
import sys

import protocolo
import jogo

#Local (por enquanto)
anel = (("127.0.0.1", 25366), 
        ("127.0.0.1", 25367), 
        ("127.0.0.1", 25368), 
        ("127.0.0.1", 25369))           

if len(sys.argv) != 2:
    print("Uso: python3 copas.py <id do player>")
    sys.exit(1)

eu = jogo.Player(int(sys.argv[1]), [])

if eu.pId not in range(4):
    print("Erro: Id invalida")
    print("Ids validas: 0, 1, 2, 3")
    sys.exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
sock.bind(anel[eu.pId])

jogo = 1;

if eu.pId == 0:
    bastao = 1
else: 
    bastao = 0
    
while jogo:
    if bastao:
        cartas = bytearray(13)
        msg = protocolo.montaMsg(protocolo.BAST, (eu.pId+1) % 4, cartas)
        sock.sendto(msg, anel[(eu.pId+1) % 4])
        print("enviei") 
        bastao = 0  
    else:
        data, addr = sock.recvfrom(1024)
        print("chegou")
        mensagem = protocolo.desmontaMsg(data)
        for i in range(4):
            print(mensagem[i])
        # bastao = 1

    
