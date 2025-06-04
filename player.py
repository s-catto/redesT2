import socket

import protocolo

PTOS_MAX = 100

class Player:
    def __init__(self, pId, prox, cartas):
        self.pId = pId
        self.prox = prox
        
        if pId == 0:
            self.bastao = 1
        else:
            self.bastao = 0 
        self.joguei = 0
        self.cartas = cartas
        self.pontos = 0
        
    def setCartas(self, cartas):
        self.cartas = cartas
        
    def joguei (self):
        self.joguei = 1
    
    def resetJoguei (self):
        self.joguei = 0
        
    def atualizaPontos (self, pontos):
        self.pontos += pontos
        if self.pontos > PTOS_MAX:
            return 1
        return 0
