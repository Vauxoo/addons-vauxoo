# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    code by rod@vauxoo.com
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

from openerp.osv import osv, fields
from datetime import datetime, timedelta
from tools.translate import _

class product_template(osv.osv):
    _inherit='product.template'
    
    
    
    _columns={
        'rent_ok':fields.boolean('Rentable'),
        'accesory_ok':fields.boolean('Accesory'),
        'rent': fields.boolean('Rent', readonly=True),
        'contract_id': fields.many2one('account.analytic.account', 'Contract', readonly=True),
    }
    
product_template()

class product_product(osv.osv):
    _inherit='product.product'
    
    _columns={
        'feature_ids': fields.one2many('product.feature.line', 'product_id', 'Features')
    }
    
product_product()

class product_feature(osv.osv):
    _name='product.feature'
    
    _columns={
        'name':fields.char('Name', size=64, required=True),
        'description':fields.char('Description', size=256),
    }
    
product_feature()

class product_feature_line(osv.osv):
    _name='product.feature.line'
    _order='product_id'
    _columns={
        'name':fields.many2one('product.feature', 'Feature', required=True),
        'product_id':fields.many2one('product.product','Product'),
        'product_line_id':fields.many2one('product.product','Product'),
        'counter':fields.integer('Counter'),
        'analytic_id':fields.many2one('account.analytic.account','Product'),
        'cost':fields.float('cost'),
        'prodlot_feature_id': fields.many2one('stock.production.lot', 'Production Lot', help="Production lot is used to put a serial number on the production", select=True),
    }
    
product_feature_line()


