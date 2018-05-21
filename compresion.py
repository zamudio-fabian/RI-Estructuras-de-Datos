# -*- coding: utf-8 -*-
from math import log

def bin_to_dec( clist , c , tot=0 ):
    """Implements ordinary binary to integer conversion if tot=0
    and HEADLESS binary to integer if tot=1
    clist is a list of bits; read c of them and turn into an integer.
    The bits that are read from the list are popped from it, i.e., deleted

    Regular binary to decimal 1001 is 9...
    >>> bin_to_dec(  ['1', '0', '0', '1']  ,  4  , 0 )
    9

    Headless binary to decimal [1] 1001 is 25...
    >>> bin_to_dec(  ['1', '0', '0', '1']  ,  4  , 1 )
    25
    """
    while (c>0) :
        assert ( len(clist) > 0 ) ## else we have been fed insufficient bits.
        tot = tot*2 + int(clist.pop(0))
        c-=1
        pass
    return tot


def dec_to_bin( n , digits ):
    """ n is the number to convert to binary;  digits is the number of bits you want
    Always prints full number of digits
    >>> print dec_to_bin( 17 , 9)
    000010001
    >>> print dec_to_bin( 17 , 5)
    10001
    
    Will behead the standard binary number if requested
    >>> print dec_to_bin( 17 , 4)
    0001
    """
    if(n<0) :
        sys.stderr.write( "warning, negative n not expected\n")
        pass
    i=digits-1
    ans=""
    while i>=0 :
        b = (((1<<i)&n)>0) 
        i -= 1
        ans = ans + str(int(b))
        pass
    return ans
    pass

def codificar_numero_vl(num):
    bytes_num = []
    while True:
        bytes_num.insert(0, num % 128)
        if num < 128:
            break
        num = num / 128
    bytes_num[len(bytes_num) - 1] += 128
    return bytes_num

# Método para codificar con Variable Length
def codificar_numeros_vl(numeros):
    bytes_numeros = []
    for num in numeros:
        bytes_num = []
        bytes_num.append(codificar_numero_vl(num))
    return bytes_numeros

# Método para decodificar con Variable Length
def decodificar_numeros_vl(bytes_numeros):
    numeros = []
    num = 0
    for i in xrange(len(bytes_numeros)):
        if bytes_numeros[i] < 128:
            num = 128 * num + bytes_numeros[i]
        else:
            num = 128 * num + (bytes_numeros[i] - 128)
            numeros.append(num)
            num = 0
    return numeros

def codificar_numero_vl_str(num):
    lista_bytes = codificar_numero_vl(num)
    str_total_bits = ""
    for byte in lista_bytes:
        str_bits = str(dec_to_bin(byte, 8))
        str_total_bits += str_bits
    return str_total_bits


def decodificar_numeros_vl_str(str_bits_numeros):
    int_numeros = []
    for i in xrange(0, len(str_bits_numeros), 8):
        str_bits_num = str_bits_numeros[i:i+8]
        int_numeros.append(convertir_a_int(str_bits_num))
    return decodificar_numeros_vl(int_numeros)


def convertir_a_bin(num):
    if num == 0:
        cantidad_bits_conversion = 1
    else:
        cantidad_bits_conversion = int(log(num, 2)) + 1
    return dec_to_bin(num, cantidad_bits_conversion)


def convertir_a_int(bits):
    str_bits = str(bits)
    return bin_to_dec(list(str_bits), len(str_bits), 0)
