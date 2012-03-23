# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
    
    def check_vat(self, cr, uid, ids, context=None):
        return all( [ self.check_vat_mx( partner.vat ) for partner in self.browse(cr, uid, ids, context=context) ] )
            
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'vat' in vals:
            vals['vat'] = vals['vat'] and vals['vat'].replace(u'-', u'').replace(u' ', u'').replace(u'.', u'').replace(u'/', u'').replace(u'ñ', u'Ñ').upper() or vals['vat']
        return super(res_partner, self).write(cr, uid, ids, vals, context=context)
        
    _constraints = [(check_vat, _(u'Error RFC es incorrecto, debería ser algo como XYZA010203A01 or XYZ0102039A8'), ["vat"])]
res_partner()
