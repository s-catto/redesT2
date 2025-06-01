M_INI = 126

# tipos 
BAST =  0
DIST =  1
JOGA =  2
FIM  =  3

def checksum (msg, tipo):
    
    if tipo == DIST:
        tam = 15
    elif tipo == JOGA:
        tam = 6
    else:
        tam = 2
        
    cs = 0   
    for i in range(0, tam):
        cs += int(msg[i])
        print(f"{msg[i]}")
        
    cs = bin(cs)
    cs = cs[2:]
    cs = cs[len(cs)-8 : len(cs)]
    
    print(f"{cs}")
         
    return int(cs, 2) 

def montaMsg (tipo, dest, cartas):
    msg = bytearray(2)
    print(msg)
    
    msg[0] = M_INI
    
    msg[1] = tipo
    msg[1] <<= 2
    msg[1] += dest
    msg[1] <<= 4  
    
    print(msg)
    
    msg.extend(cartas)
    
    print(f"{msg}")
    
    msg.append(checksum(msg, tipo))
    
    print(f"{msg}")
    
    return msg      
    

