# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from tools.translate import _

#-------------------------------------------------------------
#ENGLISH
#-------------------------------------------------------------

to_19 = ( 'Zero',  'One',   'Two',  'Three', 'Four',   'Five',   'Six',
          'Seven', 'Eight', 'Nine', 'Ten',   'Eleven', 'Twelve', 'Thirteen',
          'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen' )
tens  = ( 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety')
denom = ( '',
          'Thousand',     'Million',         'Billion',       'Trillion',       'Quadrillion',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )

# convert a value < 100 to English.
def _convert_nn(val):
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + '-' + to_19[val % 10]
            return dcap

# convert a value < 1000 to english, special cased because it is the level that kicks 
# off the < 100 special case.  The rest are more general.  This also allows you to
# get strings in the form of 'forty-five hundred' if called directly.
def _convert_nnn(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19[rem] + ' Hundred'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn(mod)
    return word

def english_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
         return _convert_nnn(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ', ' + english_number(r)
            return ret

def amount_to_text(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = english_number(int(list[0]))
    end_word = english_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and 'Cents' or 'Cent'
    final_result = start_word +' '+units_name+' and ' + end_word +' '+cents_name
    return final_result
   
    
#-------------------------------------------------------------
#SPANISH
#-------------------------------------------------------------

to_19_es = ( 'Cero',  'Uno',   'Dos',  'Tres', 'Cuatro',   'Cinco',   'Seis',
          'Siete', 'Ocho', 'Nueve', 'Diez',   'Once', 'Doce', 'Trece',
          'Catorce', 'Quince', 'Dieciseis', 'Diecisiete', 'Dieciocho', 'Diecinueve' )
tens_es  = ( 'Veinte', 'Treinta', 'Cuarenta', 'Cincuenta', 'Sesenta', 'Setenta', 'Ochenta', 'Noventa')
denom_es = ( '',
          'Mil',     'Millones',         'Billon',       'Trillon',       'Cuatrillon',
          'Quintillon' )

# convert a value < 100 to Spanish
def _convert_nn_es(val):
    if val < 20:
        return to_19_es[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_es)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' y ' + to_19_es[val % 10]
            return dcap

# convert a value < 1000 to Spanish, special cased because it is the level that kicks 
# off the < 100 special case.  The rest are more general.  This also allows you to

def _convert_nnn_es(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem ==1 :
        word='Cien'
        if mod > 0:
            word = word + 'to '
    if rem > 1:
        if rem>1 and rem < 5 or rem ==6 or rem >7 and rem < 9:
            word = to_19_es[rem] + 'cientos'
        elif rem==5:
            word = 'Quinientos'
        elif rem==7:
            word = 'Setecientos'
        else:
            word = 'Novecientos'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn_es(mod)
    return word

def spanish_number(val):
    if val < 100:
        return _convert_nn_es(val)
    if val < 1000:
         return _convert_nnn_es(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_es))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l==1:
                if didx>1:
                    ret = 'Un ' + denom_es[didx][:-2]
                else:
                    ret = 'Un ' + denom_es[didx]
            else:
                ret = _convert_nnn_es(l) + ' ' + denom_es[didx]
            if r==0 and didx>1:
                ret = ret + ' de ' 
            if r > 0:
                ret = ret + ' ' + spanish_number(r)
            return ret

def amount_to_text_es(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = spanish_number(int(list[0]))
    end_word = "%s/100"%(list[1])
    cents_number = int(list[1])
    cents_name = 'Centimos' 
    final_result = start_word +' '+units_name+' con ' + end_word +' '+cents_name
    return final_result


#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {'en' : amount_to_text, 'es' : amount_to_text_es }
    
#TODO: we should use the country AND language (ex: septante VS soixante dix)
#TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='en', currency='euro'):
    """
    Converts an integer to its textual representation, using the language set in the context if any.
    Example:
        1654: thousands six cent cinquante-quatre.
    """
    import netsvc
#    if nbr > 10000000:
#        netsvc.Logger().notifyChannel('translate', netsvc.LOG_WARNING, _("Number too large '%d', can not translate it"))
#        return str(nbr)
    
    if not _translate_funcs.has_key(lang):
        netsvc.Logger().notifyChannel('translate', netsvc.LOG_WARNING, _("no translation function found for lang: '%s'" % (lang,)))
        #TODO: (default should be en) same as above
        lang = 'en'
    return _translate_funcs[lang](abs(nbr), currency)




