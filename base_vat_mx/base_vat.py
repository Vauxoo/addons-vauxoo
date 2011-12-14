# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
############################################################################
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
from osv import osv
from osv import fields
from tools.translate import _
import re
from tools.misc import ustr
import datetime

'''
def conv_ascii(text):
    """Convierte vocales accentuadas, ñ y ç a sus caracteres equivalentes ASCII"""
    old_chars = ['á', 'é', 'í', 'ó', 'ú', 'à', 'è', 'ì', 'ò', 'ù', 'ä', 'ë', 'ï', 'ö', 'ü', 'â', 'ê', 'î', \
        'ô', 'û', 'Á', 'É', 'Í', 'Ú', 'Ó', 'À', 'È', 'Ì', 'Ò', 'Ù', 'Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'Â', 'Ê', 'Î', \
        'Ô', 'Û', 'ñ', 'Ñ', 'ç', 'Ç', 'ª', 'º', '°', ' '
    ]
    new_chars = ['a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', \
        'o', 'u', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', \
        'O', 'U', 'n', 'N', 'c', 'C', 'a', 'o', 'o', ' '
    ]
    for old, new in zip(old_chars, new_chars):
        try:
            text = text.replace(unicode(old,'UTF-8'), new)
        except:
            try:
                text = text.replace(old, new)
            except:
                raise osv.except_osv(_('Warning !'), 'No se pudo re-codificar la cadena [%s] en la letra [%s]'%(text, old) )
    return text
'''
class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    __check_vat_mx_re = re.compile(r"(?P<primeras>[A-Za-z\xd1\xf1&]{3,4})" \
                                    r"[ \-_]?" \
                                    r"(?P<ano>[0-9]{2})(?P<mes>[01][0-9])(?P<dia>[0-3][0-9])" \
                                    r"[ \-_]?" \
                                    r"(?P<code>[A-Za-z0-9&\xd1\xf1]{3})$")
    
    def check_vat_mx(self, vat):
        ''' Mexican VAT verification
        
        Verificar RFC México
        '''
        # we convert to 8-bit encoding, to help the regex parse only bytes
        if vat:
            vat = ustr(vat).encode('iso8859-1')
            m = self.__check_vat_mx_re.match(vat)
            if not m:
                #No valid format
                return False
            try:
                ano = int(m.group('ano'))
                if ano > 30:
                    ano = 1900 + ano
                else:
                    ano = 2000 + ano
                datetime.date(ano, int(m.group('mes')), int(m.group('dia')))
            except ValueError:
                return False
            #Valid format and valid date
        return True
    #check_vat = lambda *a: check_vat_mx
    
    def check_vat(self, cr, uid, ids, context=None):
        return all( [ self.check_vat_mx( partner.vat ) for partner in self.browse(cr, uid, ids, context=context) ] )
            
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        #print "vals",vals
        if 'vat' in vals:
            vals['vat'] = vals['vat'] and vals['vat'].replace('-', '').replace(' ', '').replace('.', '').replace('/','').replace('ñ','Ñ').upper() or vals['vat']
            #print "vals['vat']",vals['vat']
        #if 'active' in vals and not vals['active']:
        #if 'type' in vals.keys():
        return super(res_partner, self).write(cr, uid, ids, vals, context=context)

    
    def ____ANTERIOR2____check_vat(self, cr, uid, ids, context=None):
        '''
        Verificar RFC México
        '''
        #[IMP] base_vat: check_vat_mx by moylop260@hotmail.com, tested with 242,665 real RFC's
        import time
        import re
        map_initials = "[A-Z|&]"*4
        map_date = "[0-9][0-9][0-1][1-9][0-3][0-9]"
        map_code = "[A-Z|&|0-9]"*3
        mapping = map_initials + map_date + map_code
        for partner in self.browse(cr, uid, ids, context=context):
            vat = partner.vat
            if not vat:
                continue
            vat = conv_ascii(vat).upper().replace(' ', '').replace('-', '')
            #vat = vat.upper().replace('ñ', 'Ñ').replace('\xd1', 'Ñ').replace('\xf1', 'Ñ')#upper ascii
            #vat = vat.replace('Ñ', 'X')#Replace ascii valid char, these is problems with match in regexp
            #vat = vat.replace(' ', '').replace('-', '')#Replace some char valid, but no required
            if len(vat)==12:
                vat = "X" + vat#Add a valid char, for pass validation with case with cad of len = 12
            if len(vat) <> 13:
                return False
            regex = re.compile(mapping)
            if not regex.match(vat):
                #No valid format
                return False
            date_match = re.search(map_date, vat)
            date_format = '%y%m%d'
            try:
                time.strptime(date_match.group(), date_format)
            except:
                #Valid format, but date wrong
                return False
            #Valid format and valid date
        return True
    
    def _______ANTERIOR____check_vat(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            vat = partner.vat
            if not vat:
                continue
            vat = vat.upper()
            vat = ''.join( [x for x in vat if x.isupper() or x.isdigit() ] ) #Remove all characteres what no is digit or letter
            if len(vat)==12:
                vat = "X" + vat#Add a valid char, for pass validation with case with cad of len = 12
            if len(vat) <> 13 or not( vat[:4].isupper() 
            and vat[4:10].isdigit() and vat[10:13].isalnum() ):
                return False
        return True
    
    _constraints = [(check_vat, _('Error RFC es incorrecto, debería ser algo como XYZA010203A01 or XYZ0102039A8'), ["vat"])]
res_partner()
