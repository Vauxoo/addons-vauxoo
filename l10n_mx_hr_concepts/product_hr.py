# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: 
#    Audited by: Alejandro Negrin alejandro@openerpmexico.com
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _

from tools import config


class product_product(osv.osv):
    """
    D E S C R I P C I O N E S   de  C O L U M N A S  SOLO PARA PERCEPCIONES:							
    Proceso cálculo:  N=Nómina         M=Mensual                             (sólo en provisiones)							
    Forma de pago  :  P=Porcentaje s/Sdo. base diario     C=Cuota unit.     R=Retroactivo  I=Incap-Enferm.  N=No calcular							
    Saldo  :  A=Aumenta        D=Disminuye                           (sólo en deducciones REPETITIVAS)							
    Forma operación:  P=Sólo pesos     U=Sólo unidades   A=Ambos							
    Unidades :  D=Días           H=Horas           O=Otras           %=Porcentaje sobre sueldo base catálogo							
    Varios   :  S=Sumar a BASE DE PRODUCTIVIDAD en totales nómina    C=Calcular sdo. prom.							
    Afecta a días Trabajados Automáticos:    S=Suma      R=Resta							
    Adición séptimo:  S=Sí             N=No (igual para las últimas 4 columnas)							
    Afecta a ISPT  :  G=Grav. normal    A=Grav.Esporádico   S=Separación, compensaciones por							
                      P=Percep. anual 2-9=Grav 'n' meses  E=Exento total    N=No acumulable							
    Exento  :  No. días salario mínimo regional y concepto exento, ej: 15PV36 30AG38 15RU45							
               5/S/50% = Hasta 5 días de Sal.Mín. x SEMANA del 50% del pago (sal. mín 100%)
               1/U = 1 día de sal. mín. por UNIDAD;      90/A = 90 días de sal. mín. por año.							
    Afecta a IMSS  :  F=Fijo Sal. int   C=Comisiones      V=grav. variable   E=Exento      N=No acumulable							
    AUSENTISMO (S o R en afecta a días trab. automatic):  A=Aus.+7mo    P=Ausenc.s/7mo    I=Incapacidad							
    RETARDOS (ESPACIO en afecta a días trab. automatic):  A=Ret.+7mo    P=Retardo.s/7mo							
    Reparto utilid.:  P=Sólo pesos     U=Sólo unidades   A=Ambos           N=No acumulable							
    Bases 6, 7 y 8 :  N=No interviene para la base en cuestión							
    Control de     :  V=Vacaciones pagadas por anticipado, sueldo por.     I=Incapacidades reportadas por anticipado							
    """
    _inherit = "product.product"
    _columns = {
        'hr_concept':fields.boolean('Nomina Concept', required=False, help="Este producto estara siendo usado solo para la estimación de pagos de nomina."),
        'imprimir_rel_no':fields.boolean('Imprimir Rel. Nom.', required=False, help="Imprimir en la relación de la Nomina"),
        'imprimir_recibo':fields.boolean('Imprimir en el Recibo', required=False, help="Imprimir en Recibo de pago de la nomina"),
        'pedir_dia_en_captura':fields.boolean('Pedir dia en Captura', required=False, help="Solicitar se carguen las cantidades durante la captura"),
        'afecta_prev_social':fields.boolean('Afecta Prevision Social', required=False, help="Solicitar se carguen las cantidades durante la captura"),
        'number': fields.integer('Number', help="Used in the last sistem for internal search."),
        'forma_de_pago':fields.selection([
            ('P','Porcentaje s/Sdo. base diario'), ('C','Cuota unit.'), ('R','Retroactivo'), ('I','Incap-Enferm.'), ('N','No calcular'),
        ],'Proceso calculo', select=True, readonly=False, 
        help="Forma de pago: P=Porcentaje s/Sdo. base diario C=Cuota unit. R=Retroactivo I=Incap-Enferm. N=No calcular"),
        'valor': fields.float('Valor', digits=(16, int(config['price_accuracy'])), help="Monto Percentil del total calculado por este concepto"),
        'proceso_calculo':fields.selection([
            ('N','Nomina'), ('M','Mensual'),
        ],'Proceso de Calculo', select=True, readonly=False, 
        help="Proceso calculo:  N=Nomina M=Mensual (solo en provisiones)"),
        'saldo':fields.selection([
            ('A','Aumenta'),('D','Disminuye'),
        ],'Saldo', select=True, readonly=False,
        help="Saldo: A=Aumenta D=Disminuye (sólo en deducciones REPETITIVAS)"),
        'forma_operacion':fields.selection([
            ('P','Solo Pesos'), ('U','Solo Unidades'), ('A','Ambos'),
        ],'Forma operacion', 
        select=True, readonly=False, 
        help="Forma operación:  P=Sólo pesos     U=Sólo unidades   A=Ambos"),
        'unidades':fields.selection([
            ('D','Dias'),
            ('H','Horas'),
            ('O','Otras'),
            ('P','Porcentaje sobre sueldo base catalogo'),
        ],'Unidades', 
        select=True, 
        readonly=False, 
        help="Unidades :D=Días H=Horas O=Otras  %=Porcentaje sobre sueldo base catálogo"),
        'varios': fields.selection([
            ('S','Sumar a BASE DE PRODUCTIVIDAD en totales nomina'),
            ('C','Calcular sdo. prom.'),
        ],'Varios', 
        select=True, 
        readonly=False, 
        help="Varios: S=Sumar a BASE DE PRODUCTIVIDAD en totales nomina C=Calcular sdo. prom."),
        'afecta_dias_trab_aut': fields.selection([
            ('S','Suma'),
            ('R','Resta'),
        ],'Afecta Dias Trab. Auto.', 
        select=True, 
        readonly=False, 
        help="Afecta a dias Trabajados Automaticos: S=Suma R=Resta"),
        'adicion_septimo':fields.boolean('Adicion septimo', required=False, help="Adicion septimo: S=Si N=No (igual para las últimas 4 columnas)"),     
        'afecta_ispt': fields.selection([
            ('G','Grav. normal'),
            ('A','Grav.Esporádico'),
            ('S','Separación, compensaciones por'),
            ('P','Percep. anual'),
            ('1','Grav "1" mes'),
            ('2','Grav "2" mes'),
            ('3','Grav "3" mes'),
            ('4','Grav "4" mes'),
            ('5','Grav "5" mes'),
            ('6','Grav "6" mes'),
            ('7','Grav "7" mes'),
            ('8','Grav "8" mes'),
            ('9','Grav "9" mes'),
            ('E','Exento total'),
            ('N','No acumulable'),
        ],'Afecta a ISPT', 
        select=True, 
        readonly=False, 
        help="Afecta a ISPT: G=Grav. normal A=Grav.Esporádico S=Separación, compensaciones por P=Percep. anual 2-9=Grav 'n' meses  E=Exento total    N=No acumulable	"),
        'exento':fields.char('Exento', size=16, required=False, readonly=False, help='Exento :No. dias salario minimo regional y concepto exento, ej: 15PV36 30AG38 15RU45 5/S/50% = Hasta 5 días de Sal.Mín. x SEMANA del 50% del pago (sal. mín 100%) 1/U = 1 día de sal. min. por UNIDAD;      90/A = 90 días de sal. mín. por year.'),
        'afecta_imss': fields.selection([
            ('F','Fijo Sal. Int'),
            ('C','Comisiones'),
            ('V','Grav. Variable'),
            ('E','Exento'),
            ('N','No acumulable'),
            ('A','Aus. o Ret. +7mo'),
            ('P','Aus. o Ret. s/7mo'),
            ('I','Incapacidad'),
        ],'Afecta a IMSS',
        select=True, 
        readonly=False, 
        help="""F=Fijo Sal. int   C=Comisiones      V=grav. variable   E=Exento      N=No acumulable
AUSENTISMO (S o R en afecta a días trab. automatic):  A=Aus.+7mo    P=Ausenc.s/7mo    I=Incapacidad
RETARDOS (ESPACIO en afecta a días trab. automatic):  A=Ret.+7mo    P=Retardo.s/7mo"""),
        
        'reparto_utilid': fields.selection([
            ('P','Solo Pesos'),
            ('U','Solo Unidades'),
            ('A','Ambos'),
            ('N','No Acumulable'),
        ],'Reparto Utilidades', 
        select=True, 
        readonly=False, 
        help="Reparto utilid.: P=Sólo pesos U=Sólo unidades A=Ambos N=No acumulable"),
        
        'vacac_incap': fields.selection([
            ('V','Vacaciones'),
            ('I','Incapacidad'),
        ],'Vacaciones Incapacidad', 
        select=True, 
        readonly=False, 
        help="Columna en discusion para ser comentada"),
        
        'devolc_ispt': fields.char('DevolverISPT', size=64, select=True, readonly=False, required=False, help="Columna en discusion para ser comentada estaba vacía en toda la tabla"),
        
        'comp_cargo_poliza': fields.char('Complemento Cargo a Poliza', size=64, select=True, readonly=False, required=False, help="No esta en la documentacion...."),
        
        '__cod': fields.char('Cod',  size=64, select=True, readonly=False,  required=False, help="Cod en la tabla parece una referencia cableada revisar para colocar una relacion dura"),
    }

product_product()

class product_product(osv.osv):
    """
    product_product for deducciones
    """
    
    _inherit = 'product.product'
    _columns = {
        'saldo':fields.selection([
            ('D','Deducciones'),
            ('A','Abonos'),
        ],'Saldo', 
        select=True, 
        readonly=False, 
        help="Como es tratado el monto (solo aplicable a deducciones)"),
    }
product_product()

class product_product(osv.osv):
    """
    product_product for provisiones
    """
    
    _inherit = 'product.product'
    _columns = {
        'saldo':fields.selection([
            ('D','Deducciones'),
            ('A','Abonos'),
        ],'Saldo', 
        select=True, 
        readonly=False, 
        help="Como es tratado el monto (solo aplicable a deducciones)"),
    }
product_product()
