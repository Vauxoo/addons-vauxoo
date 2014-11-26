# -*- coding: utf-8 -*-

UNIDADES = (
    '',
    'UN ',
    'DOS ',
    'TRES ',
    'CUATRO ',
    'CINCO ',
    'SEIS ',
    'SIETE ',
    'OCHO ',
    'NUEVE ',
    'DIEZ ',
    'ONCE ',
    'DOCE ',
    'TRECE ',
    'CATORCE ',
    'QUINCE ',
    'DIECISEIS ',
    'DIECISIETE ',
    'DIECIOCHO ',
    'DIECINUEVE ',
    'VEINTE '
)
DECENAS = (
    'VENTI',
    'TREINTA ',
    'CUARENTA ',
    'CINCUENTA ',
    'SESENTA ',
    'SETENTA ',
    'OCHENTA ',
    'NOVENTA ',
    'CIEN '
)
CENTENAS = (
    'CIENTO ',
    'DOSCIENTOS ',
    'TRESCIENTOS ',
    'CUATROCIENTOS ',
    'QUINIENTOS ',
    'SEISCIENTOS ',
    'SETECIENTOS ',
    'OCHOCIENTOS ',
    'NOVECIENTOS '
)


def Numero_a_Texto(number_in):

    converted = ''

    if type(number_in) != 'str':
        number = str(number_in)
    else:
        number = number_in

    number_str = number.replace('.', '')

    try:
        number_int, number_dec = number_str.split(",")
    except ValueError:
        number_int = number_str
        number_dec = ""

    number_str = number_int.zfill(9)
    millones = number_str[:3]
    miles = number_str[3:6]
    cientos = number_str[6:]

    if(millones):
        if(millones == '001'):
            converted += 'UN MILLON '
        elif(int(millones) > 0):
            converted += '%sMILLONES ' % __convertNumber(millones)

    if(miles):
        if(miles == '001'):
            converted += 'MIL '
        elif(int(miles) > 0):
            converted += '%sMIL ' % __convertNumber(miles)
    if(cientos):
        if(cientos == '001'):
            converted += 'UN '
        elif(int(cientos) > 0):
            converted += '%s ' % __convertNumber(cientos)

    if number_dec == "":
        number_dec = "00"
    if (len(number_dec) < 2):
        number_dec += '0'

    converted += 'CON ' + number_dec + " CENTIMOS (%s)." % (number,)

    return converted


def __convertNumber(n):
    output = ''

    if(n == '100'):
        output = "CIEN "
    elif(n[0] != '0'):
        output = CENTENAS[int(n[0]) - 1]

    k = int(n[1:])
    if(k <= 20):
        output += UNIDADES[k]
    else:
        if((k > 30) & (n[2] != '0')):
            output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])

    return output
"""
print Numero_a_Texto(9121234.2)
"""
