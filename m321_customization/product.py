# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from osv import osv
from osv import fields
from tools.translate import _

class inherited_product(osv.osv):
    """
    M321 Customizations for product.product model
    """
    _inherit = "product.product"


    def _get_even_pos(self, li):
        for index in range(len(li)):
            if (index + 1) % 2 == 0:
                yield li[index]
            
    def _get_odd_pos(self, li):
        for index in range(len(li)):
            if (index + 1) % 2 != 0:
                yield li[index]
    
    
    def copy(self, cr, uid, id, default=None, context=None):
        
        if default is None:
            default = {}
        
        if context is None :
            context = {}
            
        default = default.copy()
        default.update({'upc':False,
        })
        
        return super(inherited_product, self).copy(cr, uid, id, default, context)
    
    
    
    def _find_next_ten_multi(self, value):
        while (value % 10 != 0):
            value += 1
        return value

    # Source for the validation algorithm: http://www.ehow.com/how_6810204_verify-upc-number.html
    def _check_upc(self, cr, uid, ids, context=None):
        this_record = self.browse(cr, uid, ids)
        
        if this_record[0].upc:
            if this_record[0].upc.isdigit():
                upc = map(int, this_record[0].upc)
                if len(upc) == 12:
                    check = upc[-1]
                    del(upc[-1])
                    result = (sum(tuple(self._get_odd_pos(upc))) * 3) + sum(tuple(self._get_even_pos(upc)))
                    multi_ten = self._find_next_ten_multi(result)
                    if multi_ten - result == check:
                        return True
                return False
            else:
                raise osv.except_osv(_('Error'), _('Upc code should only be numeric'))
        else:
            return True


    def _stock_available(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        if len(ids) == 0:
            return res
        for product in self.browse(cr,uid,ids,context=context):
            if product.virtual_available > 0:
                res[product.id] = 'Available'
            else:
                res[product.id] = ''
                
        return res

    _columns = {
            'upc': fields.char("UPC", size=12, help="Universal Product Code (12 digits)"),
            'available_boolean':fields.function(_stock_available, method=True,type="text", store=True, string='Available Stock'),
            'profit_code':fields.char("Code from profit", size=20, help="Code from profit database"),
        }

    _constraints =  [(_check_upc, 'ERROR, Invalid UPC', ['upc'])]


inherited_product()
