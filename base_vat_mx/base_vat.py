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

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def check_vat(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            vat = partner.vat
            if not vat:
                continue
            vat = vat.replace('-', '').replace(' ', '').replace('\n', '').replace('\r', '').replace('\r\n', '')
            if len(vat)==12:
                vat = " " + vat
            if not( vat[:3].isalpha() and vat[3:9].isdigit() and vat[-3:].isalnum() ):
                return False
        return True
res_partner()