import socket
import time

#-------- / -- / -- / --- / - / --13bytes-- / --------
# M_INI   orig  dest tipo  ack   cartas        checksum

M_INI = 126

# campos da tupla
ORIG = 0
DEST = 1
TIPO = 2
ACK  = 3
CART = 4

# tipos 
CONN =  0
BAST =  1
DIST =  2
JOGA =  3
PTOS =  4
FIM  =  5

TAM = 16

# calcula e retorna checksum de 8 bits 
def checksum (msg):
    cs = 0   
    for i in range(TAM-1):
        cs += int(msg[i])
        
    cs = bin(cs)
    cs = cs[2:]
    cs = cs[len(cs)-8 : len(cs)]
         
    return int(cs, 2) 

# checa checksum, retorna 0 caso erro
#                 retorna 1 caso certo    
def checaChecksum (msg):
    cs = msg[TAM-1]
    
    if int(cs) == checksum(msg):
        return 1
    
    return 0
        
# monta msg baseado no tipo
def montaMsg (orig, dest, tipo, ack, cartas):
    msg = bytearray(2)
    
    msg[0] = M_INI
    
    msg[1] = orig
    msg[1] <<= 2
    msg[1] += dest
    msg[1] <<= 3
    msg[1] += tipo
    msg[1] <<= 1
    msg[1] += ack
    
    
    msg.extend(bytearray(cartas))
    
    for i in range(13-len(cartas)):
        msg.append(52)
    
    msg.append(checksum(msg))
    
    return msg      

# checa e desmonta msg, retorna 0 caso erro
#                       retorna tupla caso certo   
def desmontaMsg (msg):
    if msg[0] != M_INI:
        return 0
    
    msg1 = '{0:08b}'.format(msg[1])
    
    orig = int(msg1[0:2], 2)
    
    dest = int(msg1[2:4], 2)
    
    tipo = int(msg1[4:7], 2)
    
    ack = int(msg1[7:], 2)   
       
    cartas = [0] * 13  
    for i in range(13):
        cartas[i] = int(msg[2 + i])
    
    if not checaChecksum(msg):
        return (orig, dest, -1)
    
    return (orig, dest, tipo, ack, cartas)
    

# não necessita loop externo
# monta, manda e espera ack da msg
def mandaMsg (sock, prox, euId, destId, tipo, cartas):
    msgVai = montaMsg(euId, destId, tipo, 0, cartas)
    
    ack = 0
    nAck = 1
    
    while ack == 0:
             
        if nAck: 
            sock.sendto(msgVai, prox)
        
        if tipo != FIM:    
            data, addr = sock.recvfrom(1024)
            msgVem = desmontaMsg(data)
            
            if msgVem != 0:
                if (msgVem[ACK] == 1):
                    ack = 1
                else:
                    nAck = 1
            else:
                    nAck = 0
        else:
            ack = 1
                
    return
    

# necessita loop externo
# retorna o que eh pra voce e deu ack
def esperaMsg (sock, euId, prox):

    data, addr = sock.recvfrom(1024)
    msgVem = desmontaMsg(data)
    if msgVem: 
        if FIM > msgVem[TIPO] > 0:
            if (msgVem[DEST] == euId):
                msgVai = montaMsg(msgVem[ORIG], msgVem[DEST], msgVem[TIPO], 1, msgVem[CART])
                sock.sendto(msgVai, prox)
                return msgVem
        elif msgVem[TIPO] == FIM:
            return msgVem

    sock.sendto(data, prox)
                
    return 0

# atualiza bastao e o manda p/ dest                
def passaBastao(sock, eu, destId):
    eu.bastao = 0
    mandaMsg(sock, eu.prox, eu.pId, destId, BAST, [])
    
    return
    
    
# testa anel enquanto constroi 
def conexao (sock, ant, euId, prox):
    cartas = bytearray(13)
    
    recebi = 0
    ack = 0
    nAck = 1
    
    antId = (euId+3) % 4
    proxId = (euId+1) % 4
    
    # tenta conectar com o prox, espera ack
    if euId != 3:
        msg = montaMsg(euId, proxId, CONN, 0, cartas)
        while ack == 0:
            if nAck:    
                sock.sendto(msg, prox)
            
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            
            if (mensagem != 0) & (mensagem[DEST] == euId) & (mensagem[ORIG] == proxId):
                if (mensagem[ACK] == 1):
                    ack = 1
                else:
                    nAck = 1
            else:
                nAck = 0
    
    # espera msg do anterior, envia ack        
    if euId != 0:
        recebi = 0
        while recebi == 0:
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            if (mensagem != 0) & (mensagem[DEST] == euId):
                recebi = 1 
        
        msg = montaMsg(euId, antId, CONN, 1, cartas)
        sock.sendto(msg, ant)
    
    # passada pelo anel, confirma integridade
        recebi = 0
        while recebi == 0:
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            if (mensagem != 0) & (mensagem[TIPO] == CONN):
                if (euId == 3) & (mensagem[DEST] == euId) & (mensagem[ORIG] == proxId):
                    recebi = 1
                    msg = montaMsg(euId, proxId, CONN, 1, cartas)
                    sock.sendto(msg, prox)
                else:
                    recebi = 1
                    sock.sendto(data, prox)
            
    # 0 espera ack de D, para confirmar integridade            
    else:
        msg = montaMsg(euId, 3, CONN, 0, cartas)
        sock.sendto(msg, prox)
        
        ack = 0;
        nAck = 1
        while ack == 0:
            if nAck:
                sock.sendto(msg, prox)
            
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            
            if (mensagem != 0) & (mensagem[DEST] == euId) & (mensagem[ORIG] == 3):
                if (mensagem[ACK] == 1):
                    ack = 1
                else:
                    nAck = 1
            else:
                nAck = 0
    
    return 0
    
