import socket

#-------- / -- / -- / --- / - / --13bytes-- / --------
# M_INI   orig  dest tipo  ack   cartas        checksum

M_INI = 126

# tipos 
CONN =  0
BAST =  1
DIST =  2
JOGA =  3
FIM  =  4

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
    
    msg.extend(cartas)
    
    msg.append(checksum(msg))
    
    return msg      

# checa e desmonta msg, retorna 0 caso erro
#                       retorna tupla caso certo   
def desmontaMsg (msg):
    if msg[0] != M_INI:
        return 0

    if not checaChecksum(msg):
        return 0
    
    msg1 = '{0:08b}'.format(msg[1])
    
    orig = int(msg1[0:2], 2)
    
    dest = int(msg1[2:4], 2)
    
    tipo = int(msg1[4:7], 2)
    
    ack = int(msg1[7:], 2)   
       
    cartas = bytearray(13)
    for i in range(13):
        cartas[i] = msg[2 + i]
    
    return (orig, dest, tipo, ack, cartas)

def mandaMsg (sock, eu, destId, dest, tipo, cartas):
    
    msg = montaMsg(eu, destId, tipo, 0, cartas)
    
    ack = 0
    while ack == 0:
        sock.sendto(msg, dest)
                
        data, addr = sock.recvfrom(1024)
        mensagem = desmontaMsg(data)
        
        if (mensagem != 0) & (mensagem[1] == eu) & (mensagem[0] == destId):
            if (mensagem[3] == 1):
                ack = 1
    return        
    
# testa anel enquanto constroi 
def conexao (sock, ant, eu, prox):
    cartas = bytearray(13)
    
    recebi = 0
    ack = 0
    
    antId = (eu+3) % 4
    proxId = (eu+1) % 4
    
    if eu != 3:
        mandaMsg(sock, eu, proxId, prox, CONN, cartas)
        print(f"conectei ao {proxId}")
            
    if eu != 0:    
        while recebi == 0:
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            if (mensagem != 0) & (mensagem[1] == eu) & (mensagem[0] == antId) & (mensagem[2] == 0):
                recebi = 1
                print(f"{antId} conectou")
                msg = montaMsg(eu, antId, CONN, 1, cartas)
                sock.sendto(msg, ant)
    
    
    if eu != 0:       
        recebi = 0
        while recebi == 0:
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            if (mensagem != 0) & (mensagem[2] == 0):
                if (eu == 3) & (mensagem[1] == eu) & (mensagem[0] == proxId):
                    recebi = 1
                    print("anel completo")
                    msg = montaMsg(eu, proxId, CONN, 1, cartas)
                    sock.sendto(msg, prox)
                else:
                    recebi = 1
                    print("anel completo")
                    sock.sendto(data, prox)
            
                
    elif eu == 0:
        ack = 0
        msg = montaMsg(eu, 3, CONN, 0, cartas)
        while ack == 0:
            sock.sendto(msg, prox)
            
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            
            if (mensagem != 0) & (mensagem[1] == eu) & (mensagem[0] == antId) & (mensagem[3] == 1):
                ack = 1
                print("anel completo")
    
    return 0
    
