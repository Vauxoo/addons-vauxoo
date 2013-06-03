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

class account_analytic_account(osv.osv):
    _inherit='account.analytic.account'
    
    _columns={
        'product_id':fields.many2one('product.product','Product', domain=[('rent','=',False), ('rent_ok','=',True)]),
    }
    
    def set_close(self, cr, uid, ids, context=None):
        picking_obj=self.pool.get('stock.picking')
        move_obj=self.pool.get('stock.move')
        warehouse_obj=self.pool.get('stock.warehouse')
        product_obj=self.pool.get('product.product')
        ware_id=warehouse_obj.search(cr, uid, [], context=context)[0]
        warehouse=warehouse_obj.browse(cr ,uid, ware_id, context=context)
        for contract in self.browse(cr, uid , ids , context=context):
            picking_id=picking_obj.create(cr, uid, {'origin':contract.name, 'address_id':contract.contact_id.id,'date':contract.date_start,'type':'in'}, context=context)
            move_obj.create(cr, uid, {'name':contract.product_id.name,'product_id':contract.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':contract.product_id.uom_id.id,'location_id':warehouse.lot_output_id.id,'location_dest_id':warehouse.lot_input_id.id}, context=context)
            product_obj.write(cr, uid, contract.product_id.id, {'rent':False, 'contract_id': False}, context=context)
        return super(account_analytic_account, self).set_close(cr, uid, ids, context=context)
    
    def set_open(self, cr, uid, ids, context=None):
        picking_obj=self.pool.get('stock.picking')
        move_obj=self.pool.get('stock.move')
        warehouse_obj=self.pool.get('stock.warehouse')
        product_obj=self.pool.get('product.product')
        ware_id=warehouse_obj.search(cr, uid, [], context=context)[0]
        warehouse=warehouse_obj.browse(cr ,uid, ware_id, context=context)
        
        for contract in self.browse(cr, uid , ids , context=context):
            picking_id=picking_obj.create(cr, uid, {'origin':contract.name, 'address_id':contract.contact_id.id,'date':contract.date_start,'type':'out'}, context=context)
            move_obj.create(cr, uid, {'name':contract.product_id.name,'product_id':contract.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':contract.product_id.uom_id.id,'location_id':warehouse.lot_stock_id.id,'location_dest_id':warehouse.lot_output_id.id}, context=context)
            product_obj.write(cr, uid, contract.product_id.id, {'rent':True,'contract_id':contract.id}, context=context)
        return super(account_analytic_account, self).set_open(cr, uid, ids, context=context)
    
    _defaults = {
        'state': 'draft',
    }
account_analytic_account()
    

class hr_timesheet_invoice_create(osv.osv_memory):
    _inherit='hr.timesheet.invoice.create'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(hr_timesheet_invoice_create, self).default_get(
            cr, uid, fields, context=context)
        lines=self.pool.get('account.analytic.line')
        new_ids=context.get('active_ids', [])
        line=lines.browse(cr,uid, new_ids, context=context)[0]
        res['product']=line.product_id.id
        return res
hr_timesheet_invoice_create()
        

