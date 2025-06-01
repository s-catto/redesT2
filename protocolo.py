M_INI = 126

# tipos 
BAST =  0
DIST =  1
JOGA =  2
FIM  =  3

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
def montaMsg (tipo, dest, cartas):
    msg = bytearray(2)
    
    msg[0] = M_INI
    
    msg[1] = tipo
    msg[1] <<= 2
    msg[1] += dest
    msg[1] <<= 4    # espaco para ack
    
    print(msg)
    
    msg.extend(cartas)
    
    print(f"{msg}")
    
    msg.append(checksum(msg))
    
    print(f"{msg}")
    
    return msg      

# desmonta msg, retorna 0 caso erro
#               retorna tupla caso certo   
def desmontaMsg (msg):
    checaChecksum(msg)
    
    msg1 = '{0:08b}'.format(msg[1])
    
    tipo = int(msg1[0:2], 2)
    
    dest = int(msg1[2:4], 2)
    
    ack = int(msg1[4:8], 2)   
       
    cartas = bytearray(13)
    for i in range(13):
        cartas[i] = msg[2 + i]
    
    return (tipo, dest, ack, cartas)
