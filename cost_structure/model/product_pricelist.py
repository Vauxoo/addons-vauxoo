#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import decimal_precision as dp

class inherit_price_list_item(osv.osv):
    """ """
    
    
    
    def _get_price_list(self, cr, uid, ids, field_name, arg, context=None):
        
        if context is None:
            context = {}
        versio_obj = self.pool.get('product.pricelist.version')
        price_obj = self.pool.get('product.pricelist')
        res = {}
        for item in self.browse(cr,uid,ids,context=context):
            res[item.id] = item.price_version_id and item.price_version_id.pricelist_id and \
                                                     item.price_version_id.pricelist_id.id  
            
        return res
        

    
    _inherit='product.pricelist.item'

    _columns={
    'price_list_id':fields.function(_get_price_list,method=True,type='many2one',relation='product.pricelist',string='Price LIst'),
    
    }

inherit_price_list_item()
