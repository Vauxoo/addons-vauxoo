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

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def check_vat(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            vat = partner.vat
            if not vat:
                continue
            vat = vat.upper()
            vat = ''.join( [x for x in vat if x.isupper() or x.isdigit() ] ) #Remove all characteres what no is digit or letter
            if len(vat)==12:
                vat = "X" + vat#Add a valid char, for pass validation with case with cad of len = 12
            if len(vat) <> 13 or not( vat[:4].isupper() and vat[4:10].isdigit() and vat[10:13].isalnum() ):
                return False
        return True
    
    def _construct_constraint_msg(self, cr, uid, ids, context=None):            
        return _('El RFC es incorrecto, debería ser algo como XYZA010203A01 or XYZ0102039A8')

    _constraints = [(check_vat, _construct_constraint_msg, ["vat"])]
res_partner()