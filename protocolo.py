#-------- / -- / --- / --- / --13bytes-- / --------
# M_INI    dest tipo  ack   cartas        checksum

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
def montaMsg (dest, tipo, cartas):
    msg = bytearray(2)
    
    msg[0] = M_INI
    
    msg[1] = dest
    msg[1] <<= 3
    msg[1] += tipo
    msg[1] <<= 3    # espaco para ack
    
    print(msg)
    
    msg.extend(cartas)
    
    print(f"{msg}")
    
    msg.append(checksum(msg))
    
    print(f"{msg}")
    
    return msg      

# checa e desmonta msg, retorna 0 caso erro
#                       retorna tupla caso certo   
def desmontaMsg (msg):
    if msg[0] != M_INI:
        return 0

    if not checaChecksum(msg):
        return 0
    
    msg1 = '{0:08b}'.format(msg[1])
    
    dest = int(msg1[0:2], 2)
    
    tipo = int(msg1[2:5], 2)
    
    ack = int(msg1[5:8], 2)   
       
    cartas = bytearray(13)
    for i in range(13):
        cartas[i] = msg[2 + i]
    
    return (dest, tipo, ack, cartas)
