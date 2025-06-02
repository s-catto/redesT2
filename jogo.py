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

deque = [range(52)]

def distribuicartas ():
    return
