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
    
    msg1 = '{0:08b}'.format(msg[1])
    
    orig = int(msg1[0:2], 2)
    
    dest = int(msg1[2:4], 2)
    
    tipo = int(msg1[4:7], 2)
    
    ack = int(msg1[7:], 2)   
       
    cartas = bytearray(13)
    for i in range(13):
        cartas[i] = msg[2 + i]
    
    if not checaChecksum(msg):
        return (orig, dest, -1)
    
    return (orig, dest, tipo, ack, cartas)
    

# não necessita loop externo
def mandaMsg (sock, prox, eu, destId, tipo, cartas):
    msgVai = montaMsg(eu, destId, tipo, 0, cartas)
    
    ack = 0
    nAck = 0
    while ack == 0:
        if nAck: 
            sock.sendto(msgVai, prox)
        
        data, addr = sock.recvfrom(1024)
        msgVem = desmontaMsg(data)
        
        if msgVem != 0:
            if (msgVem[3] == 1):
                ack = 1
            else:
                nAck = 1
        else:
                nAck = 0
    return
    

# necessita loop externo
def esperaMsg (sock, eu, prox):
    data, addr = sock.recvfrom(1024)
    msgVem = desmontaMsg(data)
    if msgVem != 0: 
        if msgVem[1] == eu:
            if msgVem[2] > 0:
                msgVai = montaMsg(msgVem[0], msgVem[1], msgVem[2], 1, msgVem[4])
                sock.sendto(msgVai, prox)
                return msgVem
        else:
            sock.sendto(data, prox)
                
    return 0
                
   
    
# testa anel enquanto constroi 
def conexao (sock, ant, eu, prox):
    cartas = bytearray(13)
    
    recebi = 0
    ack = 0
    nAck = 1
    
    antId = (eu+3) % 4
    proxId = (eu+1) % 4
    
    # tenta conectar com o prox, espera ack
    if eu != 3:
        msg = montaMsg(eu, proxId, CONN, 0, cartas)
        while ack == 0:
            if nAck:    
                sock.sendto(msg, prox)
            
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            
            if (mensagem != 0) & (mensagem[1] == eu) & (mensagem[0] == proxId):
                if (mensagem[3] == 1):
                    ack = 1
                    print(f"conectei ao {proxId}")
                else:
                    nAck = 1
            else:
                nAck = 0
        
    
    # espera msg do anterior, envia ack        
    if eu != 0:
        recebi = 0
        while recebi == 0:
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            if (mensagem != 0) & (mensagem[1] == eu):
                recebi = 1 
             
        print(f"{antId} conectou")
        
        msg = montaMsg(eu, antId, CONN, 1, cartas)
        sock.sendto(msg, ant)
    
    # passada pelo anel, confirma integridade
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
            
    # 0 espera ack de D, para confirmar integridade            
    else:
        msg = montaMsg(eu, 3, CONN, 0, cartas)
        sock.sendto(msg, prox)
        
        ack = 0;
        nAck = 1
        while ack == 0:
            if nAck:
                sock.sendto(msg, prox)
            
            data, addr = sock.recvfrom(1024)
            mensagem = desmontaMsg(data)
            
            if (mensagem != 0) & (mensagem[1] == eu) & (mensagem[0] == 3):
                if (mensagem[3] == 1):
                    ack = 1
                    print("anel completo")
                else:
                    nAck = 1
            else:
                nAck = 0
    
    return 0
    
