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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class analytic_term(osv.osv):
    _name='analytic.term'
    
    _columns={
        'name': fields.char('Term',size=64,required=True),
        'no_term': fields.integer('No Term')
    }

class account_analytic_product(osv.osv):
    _name='account.analytic.product'
    
    _columns={
        'product_id':fields.many2one('product.product','Product', domain=[('rent','=',False), ('rent_ok','=',True)]),
        'analytic_id':fields.many2one('account.analytic.account','Account Analytic')
    }

class account_analytic_line(osv.osv):
    _inherit='account.analytic.line'
    
    def _check_inv(self, cr, uid, ids, vals):
        print ids,vals,'pero si entra'
        select = ids
        if isinstance(select, (int, long)):
            print "si lo hace"
            select = [ids]
        if ( not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                if line.invoice_id and 'account_id' not in vals:
                    print line.invoice_id,line.id, "no tiene"
                    raise osv.except_osv(_('Error !'),
                        _('You cannot modify an invoiced analytic lines!'))
        return True
    
    def onchange_copys(self, cr, uid, id, w_start, w_end, context=None):
        res={}
        if context==None:
            context={}
        return {'value':{'unit_amount': w_end - w_start} }
    
    _columns={
        'w_start': fields.integer('Inicial'),
        'w_end': fields.integer('Final'),
    }


class account_analytic_account(osv.osv):
    _inherit='account.analytic.account'
    
    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        for contract in self.browse(cr, uid, ids, context=context):
            src = []
            lines = []
            for line in contract.line_ids:
                if line.invoice_id:
                    if line.invoice_id.state=='paid':
                        for l in line.invoice_id.payment_ids:
                            if l.id not in lines:
                                lines.append(l.id)
            result[contract.id] = lines
        print result,"lo mismos"
        return result
        
    def _compute_lines_inv(self, cr, uid, ids, name, args, context=None):
        result = {}
        for contract in self.browse(cr, uid, ids, context=context):
            src = []
            lines = []
            for line in contract.line_ids:
                if line.invoice_id and line.invoice_id.id not in lines:
                    lines.append(line.invoice_id.id)
            print lines,"lines"
            result[contract.id]=lines
        print result,"si sale"
        return result
    
    _columns={
        'product_ids':fields.one2many('account.analytic.product','analytic_id', 'Products'),
        'term_id': fields.many2one('analytic.term','Term'),
        'voucher_ids': fields.function(_compute_lines, relation='account.move.line', type="many2many", string='Payments'),
        'invoice_ids': fields.function(_compute_lines_inv, relation='account.invoice', type="many2many", string='Invoice'),
        'group_product': fields.boolean('Group Product')
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
            for prod in contract.product_ids:
                move_obj.create(cr, uid, {'name':prod.product_id.name,'product_id':prod.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':prod.product_id.uom_id.id,'location_id':warehouse.lot_output_id.id,'location_dest_id':warehouse.lot_input_id.id}, context=context)
                product_obj.write(cr, uid, prod.product_id.id, {'rent':False, 'contract_id': False}, context=context)
        return super(account_analytic_account, self).set_close(cr, uid, ids, context=context)
    
    def set_open(self, cr, uid, ids, context=None):
        picking_obj=self.pool.get('stock.picking')
        move_obj=self.pool.get('stock.move')
        warehouse_obj=self.pool.get('stock.warehouse')
        product_obj=self.pool.get('product.product')
        line_obj=self.pool.get('account.analytic.line')
        ware_id=warehouse_obj.search(cr, uid, [], context=context)[0]
        warehouse=warehouse_obj.browse(cr ,uid, ware_id, context=context)
        
        for contract in self.browse(cr, uid , ids , context=context):
            date_invoice=contract.date_start
            #~ date_invoice=datetime.strptime(contract.date_start, "%Y-%m-%d")
            picking_id=picking_obj.create(cr, uid, {'origin':contract.name, 'address_id':contract.contact_id.id,'date':contract.date_start,'type':'out'}, context=context)
            for prod in contract.product_ids:
                move_obj.create(cr, uid, {'name':prod.product_id.name,'product_id':prod.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':prod.product_id.uom_id.id,'location_id':warehouse.lot_stock_id.id,'location_dest_id':warehouse.lot_output_id.id}, context=context)
            for line in range(0,contract.term_id.no_term):
                for prod in contract.product_ids:
                    for feature in prod.product_id.feature_ids:
                        line_obj.create(cr, uid, {'date':date_invoice,'name':feature.name.name,'product_id':prod.product_id.id,'product_uom_id':prod.product_id.uom_id.id,'general_account_id':105,'to_invoice':1,'account_id':contract.id,'journal_id':2},context=context)
                    product_obj.write(cr, uid, prod.product_id.id, {'rent':True,'contract_id':contract.id}, context=context)
                date_invoice=(datetime.strptime(date_invoice, "%Y-%m-%d") + relativedelta(months=1)).strftime("%Y-%m-%d")
        return super(account_analytic_account, self).set_open(cr, uid, ids, context=context)
    
    _defaults = {
        'state': 'draft',
        'group_product': True
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
        

