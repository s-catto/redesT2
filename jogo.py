import random
import time

import protocolo

class Player:
    def __init__(self, pId, prox, cartas):
        self.pId = pId
        self.prox = prox
        if pId == 0:
            self.bastao = 1
        else:
            self.bastao = 0 
        self.cartas = cartas
        
    def setCartas(self, cartas):
        self.cartas = cartas
    
#================================================

class Cores:
    PRETO = "\033[38;2;0;0;0;48;2;255;255;255m"
    VERM  = "\033[38;2;255;0;0;48;2;255;255;255m"
    RESET = "\033[0m"

cartas = ["A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
         "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
         "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
         "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

deque = list(range(52))

def distribuiCartas (sock, eu):
    
    random.shuffle(deque)
    
    # time.sleep(1)
    
    for i in range(0,4):
        cartas = deque[i*13:(i*13)+13]
        if i != eu.pId:
            protocolo.mandaMsg(sock, eu.prox, eu.pId, i, protocolo.DIST, cartas) 
        else:
            eu.cartas = cartas       
    
    return
    
def esperaCartas (sock, eu):
    
    recebi = 0
    while not recebi:
        msgVem = protocolo.esperaMsg(sock, eu.pId, eu.prox)
        if (msgVem):
            if (msgVem[protocolo.TIPO] == protocolo.DIST):
                eu.cartas = msgVem[protocolo.CART]
                recebi = 1
           
    return 
        
