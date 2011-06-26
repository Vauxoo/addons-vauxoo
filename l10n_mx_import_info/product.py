# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Nhomar Hernandez nhomar@vauxoo.com
#
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
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _


class product_import_info(osv.osv):
    _name = 'product.import.info'
    _rec_name = 'import_id'
    _columns = {
            'product_id': fields.many2one('product.product','Product',required=True,
            help="Product to be counted on this Import Document information"),
            'import_id': fields.many2one('import.info','Import Info', required=True,
            help="Import Document related"),
            'qty': fields.float('Quantity', (16,4), 
            help="Quantity of this product on this document,"),
            'uom_id':fields.many2one('product.uom', 'UoM', required=False,
            help="Unit of measure, be care this unit must be on the same category of unit indicated on the product form,"),
    }
    _defaults = {
    }
    
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        """
        Return a dict that contains new values, and context
    
        @param cr: cursor to database
        @param user: id of current user
        @param product_id: latest value from user input for field product_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        
        @return: return a dict that contains new values, and context
        """
        res={}
        if product_id:
            res={'value':{'uom_id': self.pool.get('product.product').browse(cr,uid,product_id,context).uom_po_id.id
                }}
        return res
product_import_info()


class product_product(osv.osv):
    """
    product_product
    """
    _inherit = 'product.product'
    _columns = {
        'pack_control':fields.boolean('Pack Control', required=False,
        help="If you wnat to track import information to be used on invoices and other documents check this field, remember, if the product is a service this information can not be tracked, if this field is checked you will need to use consumable or stockable type of product on information page."),
        'import_info_ids':fields.one2many('product.import.info', 'product_id', 'Import Info', required=False),
    }
product_product()
