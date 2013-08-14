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
    

    def onchange_prodlot(self, cr , uid, ids, prodlot_id, context=None):
        if context==None:
            context={}
        res={}
        if prodlot_id:
            prodlot_obj=self.pool.get('stock.production.lot')
            if prodlot_obj.browse(cr, uid, prodlot_id, context=context).stock_available < 0:
                res={'value':{'prodlot_id': False },'warning':{
                'title': _('This product is already rented  !'),
                'message': _('This product is already rented,check serial number.')
            }}
        return res
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res={}
        list=[]
        if context==None:
            context={}
        if product_id:
            product_obj=self.pool.get('product.product')
            for prod in product_obj.browse(cr, uid, [product_id], context):
                type='rent'
                if prod.accesory_ok:
                    type='accesory'
                list_data = [{'name':feature.name.id} for feature in prod.feature_ids]
            res={'value':{'type': type, }}
        return res
    
    _columns={
        'product_id':fields.many2one('product.product','Product', required=True, domain=['|', ('rent_ok','=',True), ('accesory_ok','=',True) ]),
        'type': fields.selection([('rent','Rent'),('accesory','Accesory')],'Type'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', help="Production lot is used to put a serial number on the production", select=True),
        'analytic_id':fields.many2one('account.analytic.account','Account Analytic')
    }

class account_analytic_line(osv.osv):
    _inherit='account.analytic.line'
    _order='product_id'
    
    def _check_inv(self, cr, uid, ids, vals):
        select = ids
        if isinstance(select, (int, long)):
            select = [ids]
        if ( not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                if line.invoice_id and 'account_id' not in vals:
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
        'feature_id': fields.many2one('product.feature.line','Feature')
    }


class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'
    
    _columns={
        'w_start': fields.integer('Inicial'),
        'w_end': fields.integer('Final'),
    }
account_invoice_line()
    

class account_analytic_account(osv.osv):
    _inherit='account.analytic.account'
    
    def onchange_product_lines(self, cr, uid, ids, product_ids, feature_ids, context=None):
        res={}
        list_feature=[]
        if context==None:
            context={}
        if product_ids:
            product_obj=self.pool.get('product.product')
            for prod in product_ids:
                if prod[2]['product_id']:
                    for feature in product_obj.browse(cr, uid, prod[2]['product_id'], context=context).feature_ids:
                        list_feature.append({'name':feature.name.id, 'product_line_id':prod[2]['product_id'],'counter':feature.counter})
        return {'value':{'feature_ids': [(0, 6, data) for data in list_feature]}}

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        type_inv = context.get('type', 'out_invoice')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'sale')),
                                            ('company_id', '=', company_id)],
                                                limit=1)
        return res and res[0] or False
    
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
        return result
        
    def _compute_lines_inv(self, cr, uid, ids, name, args, context=None):
        result = {}
        for contract in self.browse(cr, uid, ids, context=context):
            src = []
            lines = []
            for line in contract.line_ids:
                if line.invoice_id and line.invoice_id.id not in lines:
                    lines.append(line.invoice_id.id)
            result[contract.id]=lines
        return result
    
    _columns={
        'product_ids':fields.one2many('account.analytic.product','analytic_id', 'Products'),
        'term_id': fields.many2one('analytic.term','Term', required=True),
        'voucher_ids': fields.function(_compute_lines, relation='account.move.line', type="many2many", string='Payments'),
        'invoice_ids': fields.function(_compute_lines_inv, relation='account.invoice', type="many2many", string='Invoice'),
        'group_product': fields.boolean('Group Product'),
        'journal_id':fields.many2one('account.journal','Journal', required=True),
        'feature_ids': fields.one2many('product.feature.line', 'analytic_id', 'Features')
    }
    
    def set_close(self, cr, uid, ids, context=None):
        picking_obj=self.pool.get('stock.picking')
        move_obj=self.pool.get('stock.move')
        warehouse_obj=self.pool.get('stock.warehouse')
        product_obj=self.pool.get('product.product')
        ware_id=warehouse_obj.search(cr, uid, [], context=context)[0]
        warehouse=warehouse_obj.browse(cr ,uid, ware_id, context=context)
        location = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'customer')], context=context)
        if location:
            location=location[0]
        else:
            raise osv.except_osv(_('Error!'),  _('You not have a configured client location'))
        for contract in self.browse(cr, uid , ids , context=context):
            picking_id=picking_obj.create(cr, uid, {'origin':contract.name, 'address_id':contract.contact_id.id,'date':contract.date_start,'type':'in'}, context=context)
            for prod in contract.product_ids:
                move_obj.create(cr, uid, {'name':prod.product_id.name,'product_id':prod.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':prod.product_id.uom_id.id,'location_id':location,'location_dest_id':warehouse.lot_input_id.id, 'prodlot_id':prod.prodlot_id.id}, context=context)
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
                move_obj.create(cr, uid, {'name':prod.product_id.name,'product_id':prod.product_id.id,'product_qty':1,'picking_id':picking_id,'product_uom':prod.product_id.uom_id.id,'location_id':warehouse.lot_stock_id.id,'location_dest_id':warehouse.lot_output_id.id, 'prodlot_id':prod.prodlot_id.id}, context=context)
            for line in range(0,contract.term_id.no_term):
                for prod in contract.product_ids:
                    a = prod.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = prod.product_id.categ_id.property_account_income_categ.id
                    for feature in contract.feature_ids:
                        if feature.product_line_id.id==prod.product_id.id:
                            line_obj.create(cr, uid, {'date':date_invoice,'name':feature.name.name,'product_id':prod.product_id.id,'product_uom_id':prod.product_id.uom_id.id,'general_account_id':a,'to_invoice':1,'account_id':contract.id,'journal_id':contract.journal_id.analytic_journal_id.id,'amount':feature.cost, 'feature_id':feature.id},context=context)
                    product_obj.write(cr, uid, prod.product_id.id, {'rent':True,'contract_id':contract.id}, context=context)
                date_invoice=(datetime.strptime(date_invoice, "%Y-%m-%d") + relativedelta(months=1)).strftime("%Y-%m-%d")
        return super(account_analytic_account, self).set_open(cr, uid, ids, context=context)
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('account.journal')
        if context is None:
            context = {}
        res = super(account_analytic_account,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = 'sale'
        for field in res['fields']:
            if field == 'journal_id' and type:
                journal_select = journal_obj._name_search(cr, uid, '', [('type', '=', type)], context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select

        return res
    
    _defaults = {
        'state': 'draft',
        'group_product': True,
        'journal_id': _get_journal,
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
        

