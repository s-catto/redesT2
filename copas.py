import socket
import sys

class Player:
    def __init__(self, pId, cartas):
        self.pId = pId
        self.prox = (pId + 1) % 4
        self.cartas = cartas
        
    def setCartas(self, cartas):
        self.cartas = cartas
    

#================================================

class Cores:
    PRETO = "\033[38;2;0;0;0;48;2;255;255;255m"
    VERM  = "\033[38;2;255;0;0;48;2;255;255;255m"
    RESET = "\033[0m"

deque = ["A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
         "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
         "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
         "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

#Local (por enquanto)
anel = (("127.0.0.1", 25366), 
         ("127.0.0.1", 25367), 
         ("127.0.0.1", 25368), 
         ("127.0.0.1", 25369))           

if len(sys.argv) != 2:
    print("Uso: python3 copas.py <id do player>")
    sys.exit(1)

eu = Player(int(sys.argv[1]), [])

if not ( 0 <= eu.pId < 4):
    print("Erro: Id invalida")
    print("Ids validas: 0, 1, 2, 3")
    sys.exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
sock.bind(anel[eu.pId])

jogo = 1;

if eu.pId == 0:
    bastao = 1;
    while jogo:
        if bastao:
            sock.sendto(b"eba!", anel[(eu.pId+3) % 4])
            print("enviei") 
            bastao = 0  
        else:
            data, addr = sock.recvfrom(1024)
            print(data.decode("utf-8"))
            bastao = 1

else:
    bastao = 0;
    while jogo:
        if bastao:
            sock.sendto(b"eba!", anel[(eu.pId+3) % 4])
            print("enviei")
            bastao = 0
        else:
            data, addr = sock.recvfrom(1024) 
            print(data.decode("utf-8"))   
            bastao = 1

    
