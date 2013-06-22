#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <humbertoarocha@gmail.com>
#    Audited by: Nhomar Hernandez <nhomar@gmail.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools

#----------------------------------------------------------
# Periodic Inventory Valuation
#----------------------------------------------------------

class periodic_inventory_valuation(osv.osv):
    _name = "periodic.inventory.valuation.line"
    _description = "Periodic Inventory Valuation Lines"
    _rec_name='product_id'
    _columns = {
        'piv_id':fields.many2one('periodic.inventory.valuation', 'Valuation Document', help='Valuation Document to which this line belogs'), 
        'product_id':fields.many2one('product.product', 'Product', help='Product to be Valuated in this Document'), 
        'qty':fields.float('Quantity', help='Product Quantity'), 
        'uom_id':fields.many2one('product.uom', 'Unit of Measure', help='Product Unit of Measure being used to compute Inventory Valuation'), 
        'valuation':fields.float('Product Valuation', help='Product Valuation'), 
        'company_id':fields.related('piv_id', 'company_id', string='Company',
            relation='res.company', type='many2one', store=True, help='Company for this Document Line'), 
        'currency_id':fields.related('piv_id', 'company_id', 'currency_id', string='Company',
            relation='res.currency', type='many2one', store=True, help='Currency to be used when creating Journal Entries and Accounting Entries'), 
        'period_id':fields.related('piv_id', 'period_id', string='Company',
            relation='account.period', type='many2one', store=True, help='Company for this Document Line'), 
        'date':fields.related('piv_id', 'date', string='Company',
            type='date', store=True, help='Date to be used when creating Journal Entries and Accounting Entries'), 
    }

class periodic_inventory_valuation(osv.osv):
    _name = "periodic.inventory.valuation"
    _description = "Periodic Inventory Valuation"
    _columns = {
        'name': fields.char('Name', size=64, required=True, help=""),
        'move_id':fields.many2one('account.move', 'Journal Entry', help='Journal Entry For this Periodic Inventory Valuation Document, it will be created when Document is Posted'), 
        'company_id':fields.many2one('res.company', 'Company', help='Company for this Document'), 
        'period_id':fields.many2one('account.period', 'Period', help='Accounting Period to be used when creating Journal Entries and Accounting Entries'), 
        'journal_id':fields.many2one('account.journal', 'Journal', help='Accounting Journal to be used when creating Journal Entries and Accounting Entries'),         
        'currency_id':fields.many2one('res.currency', 'Currency', help='Currency to be used when creating Journal Entries and Accounting Entries'),                 
        'date':fields.date('Valuation Date', help='Date to be used when creating Journal Entries and Accounting Entries'), 
        'state':fields.selection([('draft','Readying Valuation'),('confirm','Ready to Valuate'),('done','Valuated Inventory')]), 
        'product_ids':fields.many2many('product.product', 'piv_prod_rel', 'product_id', 'piv_id', 'Valuating Products', help='Products to be Valuated'), 
        'stock_move_ids':fields.many2many('stock.move', 'piv_sm_rel', 'stock_move_id', 'piv_id', 'Stock Moves', help='Stock Moves to be used as Control Sample'), 
        'ail_ids':fields.many2many('account.invoice.line', 'piv_ail_rel', 'ail_id', 'piv_id', 'Account Invoice Lines', help='Account Invoice Lines to be used to Valuate Inventory'), 
        'aml_ids':fields.many2many('account.move.line', 'piv_aml_rel', 'aml_id', 'piv_id', 'Account Move Lines', help='Account Move Lines to be Created to Valuate Inventory'), 
        'pivl_ids':fields.many2one('periodic.inventory.valuation.line', 'piv_id', 'Periodic Inventory Valuation Lines', help='Periodic Inventory Valuation Lines created to valuate Inventory'), 
    }
