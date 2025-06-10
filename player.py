import socket

import protocolo

# estados

MESTRE = 0
COMUM  = 1

class Player:
    def __init__(self, pId, prox, cartas):
        self.pId = pId
        self.prox = prox
        
        if pId == 0:
            self.bastao = 1
            self.estado = MESTRE
        else:
            self.bastao = 0 
            self.estado = COMUM
            
        self.joguei = 0
        self.cartas = cartas
        self.pontos = 0
        
    def setCartas(self, cartas):
        self.cartas = cartas
     
    def setEstado(self, estado):
        self.estado = estado
     
    def setJoguei (self):
        self.joguei = 1
    
    def resetJoguei (self):
        self.joguei = 0
        
    def atualizaPontos (self, pontos):
        self.pontos += pontos
