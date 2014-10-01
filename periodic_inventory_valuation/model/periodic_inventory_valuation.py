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
import datetime

#----------------------------------------------------------
# Periodic Inventory Valuation
#----------------------------------------------------------

class account_invoice_line(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
            'currency_id':fields.related('invoice_id', 'currency_id', relation='res.currency', type='many2one', string='Currency', help='field'), 
            }

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
            'inventory_valuation_journal_id': fields.many2one('account.journal', 'Periodical Inventory Valuation Journal', required=True, help="Journal entry"),
            }
    
class periodic_inventory_valuation_line(osv.osv):
    _name = "periodic.inventory.valuation.line"
    _description = "Periodic Inventory Valuation Lines"
    _rec_name='product_id'
    _columns = {
        'piv_id':fields.many2one('periodic.inventory.valuation', 'Valuation Document', help='Valuation Document to which this line belogs'), 
        'product_id':fields.many2one('product.product', 'Product', help='Product to be Valuated in this Document'), 
        'qty_final':fields.float('Quantity Final', help='Product Quantity Final'), 
        'qty_init':fields.float('Quantity Initial', help='Product Quantity Initial'), 
        'qty_sale':fields.float('Quantity Sales', help='Product Quantity Sales'), 
        'qty_purchase':fields.float('Quantity Purchases', help='Product Quantity Purchases'), 
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
        'average_cost':fields.float('Average Cost', help='Is the average cost of the product'),
    }

class periodic_inventory_valuation(osv.osv):
    _name = "periodic.inventory.valuation"
    _description = "Periodic Inventory Valuation"
    _columns = {
        'name': fields.char('Name', size=64, required=True, help=""),
        'move_id':fields.many2one('account.move', 'Journal Entry', help='Journal Entry For this Periodic Inventory Valuation Document, it will be created when Document is Posted'), 
        'company_id':fields.many2one('res.company', 'Company', help='Company for this Document'), 
        'period_id':fields.many2one('account.period', 'Period', help='Accounting Period to be used when creating Journal Entries and Accounting Entries'), 
        'inventory_valuation_journal_id':fields.many2one('account.journal', 'Journal', help='Accounting Journal to be used when creating Journal Entries and Accounting Entries'),         
        'currency_id':fields.many2one('res.currency', 'Currency', help='Currency to be used when creating Journal Entries and Accounting Entries'),                 
        'date':fields.date('Valuation Date', help='Date to be used when creating Journal Entries and Accounting Entries'), 
        'state':fields.selection([('draft','Readying Valuation'),('confirm','Ready to Valuate'),('done','Valuated Inventory')]), 
        'product_ids':fields.many2many('product.product', 'piv_prod_rel', 'product_id', 'piv_id', 'Valuating Products', help='Products to be Valuated'), 
        'stock_move_ids':fields.many2many('stock.move', 'piv_sm_rel', 'stock_move_id', 'piv_id', 'Stock Moves', help='Stock Moves to be used as Control Sample'), 
        'ail_ids':fields.many2many('account.invoice.line', 'piv_ail_rel', 'ail_id', 'piv_id', 'Account Invoice Lines', help='Account Invoice Lines to be used to Valuate Inventory'), 
        'aml_ids':fields.many2many('account.move.line', 'piv_aml_rel', 'aml_id', 'piv_id', 'Account Move Lines', help='Account Move Lines to be Created to Valuate Inventory'), 
        'pivl_ids':fields.one2many('periodic.inventory.valuation.line', 'piv_id', 'Periodic Inventory Valuation Lines', help='Periodic Inventory Valuation Lines created to valuate Inventory'), 
        'first':fields.boolean('First run'),
        }
    _defaults = {
        'state': 'draft',
        'company_id': lambda s, c, u, ctx: \
            s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.id,
        'first': False,
        'currency_id': lambda s, c, u, ctx: \
            s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.currency_id.id,
        'inventory_valuation_journal_id': lambda s, c, u, ctx: \
            s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.inventory_valuation_journal_id.id,
       }

    def get_period(self, cr, uid, ids, date,context=None):
        if context is None:
            context = {}
        
        period_obj = self.pool.get('account.period')
        period_ids = period_obj.find(cr,uid,dt=date,context=context)
        period_ids = period_obj.search(cr,uid,[
            ('id','in',period_ids),('special','=',False)],context=context)
        period_ids = period_ids and period_ids[0] or False
        if not period_ids:
            raise osv.except_osv(_('Error!'), _('There is no fiscal year defined for this date.\nPlease create one from the configuration of the accounting menu.'))
        
        return period_ids
   
    def exchange(self, cr, uid, ids, from_amount, to_currency_id, from_currency_id, exchange_date, context=None):                                  
        if context is None:                                                     
            context = {}                                                        
        if from_currency_id == to_currency_id:                                  
            return from_amount                                                  
        curr_obj = self.pool.get('res.currency')                                
        context['date'] = exchange_date                                         
        return curr_obj.compute(cr, uid, from_currency_id, to_currency_id, from_amount, context=context)

    def validate_data(self, cr, uid, ids, date, context=None):
        if context is None:
            context = {}
        
        if ids:
            if type(ids) is list:
                peri_inv_allowed = self.search(cr, uid, [('id','!=',ids[0])], order='id desc', limit=1, context=context)
            else:
                peri_inv_allowed = self.search(cr, uid, [('id','!=',ids)], order='id desc', limit=1, context=context)
        else:
            peri_inv_allowed = self.search(cr, uid, [], order='id desc', limit=1, context=context)

        all_per_inv = self.browse(cr, uid, peri_inv_allowed, context=context)
        #$$$         
        for i in all_per_inv:
            if date <= i.date:
                raise osv.except_osv('Record with this data existing !', 'Can not create a record with repeated date')
        
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:                                                     
            context = {}         
        
        if type(ids) is list:
            brw_per_inv = self.browse(cr, uid, ids[0], context=context)
        else:
            brw_per_inv = self.browse(cr, uid, ids, context=context)
        
        if brw_per_inv.state == 'done':
            raise osv.except_osv('Can not write the record', 'When a stock is done, can not be write')
        
        self.validate_data(cr, uid, ids, brw_per_inv.date,context=context)
        
        vals['period_id'] = self.get_period(cr, uid, ids, vals.get('date'), context=context)
        return super(periodic_inventory_valuation, self).write(cr, uid, ids, vals, context=context)        

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        
        inv = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.inventory_valuation_journal_id
        if not inv.id:    
            raise osv.except_osv('You need to define the journal', 'Must be defined in the company the journal to generate the journal items for periodic inventory')

        self.validate_data(cr, uid, False, vals.get('date'),  context=context)
        vals['period_id'] = self.get_period(cr, uid, False, vals.get('date'), context=context)
        return super(periodic_inventory_valuation, self).create(cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        brw_per_inv = self.browse(cr, uid, ids[0], context=context)
        
        if brw_per_inv.state == 'done':
            raise osv.except_osv('Can not delete the record', 'When a stock is done, can not be deleted')

        return super(periodic_inventory_valuation, self).unlink(cr, uid, ids, context=context)

    def load_valuation_items(self, cr, uid, ids, context=None):
        context = context or {} 
        ids = isinstance(ids, (int, long)) and [ids] or ids
        prod_obj = self.pool.get('product.product')

        prod_ids = prod_obj.search(cr,uid,[
            ('type','=','product'),('valuation','=','manual_periodic'),
            ],context=context)
        
        period_obj = self.pool.get('account.period')
        piv_brw = self.browse(cr,uid,ids[0],context=context)
        date = piv_brw.date
        company_id = piv_brw.company_id.id 
        currency_id = piv_brw.currency_id.id

        inventory_valuation_journal_id = piv_brw.company_id.inventory_valuation_journal_id.id

        period_id = piv_brw.period_id.id

        inv_obj = self.pool.get('account.invoice')
        
        #Se obtiene la linea del producto del registro anterior
        if type(ids) is list:
            piv_id = self.search(cr, uid, [('id','!=',ids[0]),('state','=','done')], order='id desc', limit=1, context=context)
        else:
            piv_id = self.search(cr, uid, [('id','!=',ids),('state','=','done')], order='id desc', limit=1, context=context)
        
        piv = self.browse(cr,uid,ids[0],context=context)
        fecha_now = datetime.datetime.strptime(piv.date, '%Y-%m-%d')

        if piv_id:
            piv_id = piv_id[0]
            piv_before = self.browse(cr, uid, piv_id, context=context)
            fecha_before = datetime.datetime.strptime( piv_before.date ,'%Y-%m-%d')
        else:
            fecha_before = False 

        inv_ids = []

        if fecha_before:
             inv_ids = inv_obj.search(cr,uid,[                                       
                    ('state','in',('open','paid')),
                    ('date_invoice','>',fecha_before),('date_invoice','<=',fecha_now),   
                    ('company_id','=',company_id)                                       
                    ],context=context) 
        else:
             inv_ids = inv_obj.search(cr,uid,[                                       
                    ('state','in',('open','paid')),
                    ('date_invoice','<=',fecha_now),   
                    ('company_id','=',company_id)                                       
                    ],context=context) 
            
        if not inv_ids:
            raise osv.except_osv(_('Error!'), _('There are no invoices defined for this period.\nMake sure you are using the right date.'))
        ail_obj = self.pool.get('account.invoice.line')
        ail_ids = ail_obj.search(cr,uid,[
            ('invoice_id','in',inv_ids),('product_id','in',prod_ids)
            ],context=context)
        if not ail_ids:
            raise osv.except_osv(_('Error!'), _('There are no invoices lines defined for this period.\nMake sure you are using the right date.'))

        period_brw = period_obj.browse(cr,uid,period_id,context=context)
        date_start = period_brw.date_start
        date_stop = period_brw.date_stop

        sl_obj = self.pool.get('stock.location')
        int_sl_ids = sl_obj.search(cr,uid,[('usage','=','internal')],context=context)
        ext_sl_ids = sl_obj.search(cr,uid,[('usage','!=','internal')],context=context)

        sm_obj = self.pool.get('stock.move')
        incoming_sm_ids = sm_obj.search(cr,uid,[
            ('state','=','done'),('company_id','=',company_id),
            ('location_id','in',ext_sl_ids),('location_dest_id','in',int_sl_ids),
            ('date','>=',date_start),('date','<=',date_stop),
            ],context=context)
        outgoing_sm_ids = sm_obj.search(cr,uid,[
            ('state','=','done'),('company_id','=',company_id),
            ('location_id','in',int_sl_ids),('location_dest_id','in',ext_sl_ids),
            ('date','>=',date_start),('date','<=',date_stop),
            ],context=context)

        #Se establecen parametros para usar en los calculos
        periodic_line = self.pool.get('periodic.inventory.valuation.line')
        lineas = []
        move_id = False
        state = 'draft'




        #Si no se han hecho calculos, se cargan datos iniciales, aqui la condicion deberia ser si el estado es draft
        #Se debe validar que si es el primer registro cargar datos en 0, si no es el primer registro entonces tomar
        #valores del ultimo registro
        if not piv.first:
            state = 'confirm'
            
            pivline_init_ids = []
            #Se itera sobre los productos que sean de tipo producto y con valuation tipo manual_periodic
            for prod_id in prod_ids:
                prod = prod_obj.browse(cr,uid,prod_id,context=context)
                
                piv_line_id = False

                if piv_id:
                    piv_line_id = periodic_line.search(cr, uid, [('piv_id','=',piv_id),('product_id','=',prod_id)], context=context)
                
                #condicional aqui de piv_line_brw, puede que no exista 
                if piv_line_id:
                    piv_line_brw = periodic_line.browse(cr, uid, piv_line_id, context=context)[0]
                    line_qty_init = piv_line_brw.qty_final
                    line_average_cost = piv_line_brw.average_cost
                    line_valuation = piv_line_brw.valuation
                else:
                    line_qty_init = 0.0
                    line_average_cost = 0.0 
                    line_valuation = 0.0
                
                #Guardar informacion de la linea piv a crear en el registro actual
                pivline_init_ids.append(periodic_line.create(cr, uid, {
                        'piv_id': ids[0],
                        'product_id':prod_id,
                        'qty_init':line_qty_init,
                        'qty_final':0.0,
                        'qty_sale':0.0,
                        'qty_purchase':0.0,
                        'uom_id':prod.uom_id.id,
                        'average_cost':line_average_cost,
                        'valuation':line_valuation,
                        }, context=context))
                
            #Cargar lineas nuevas en el registro actual
            self.write(cr,uid,ids[0],{
                'pivl_ids':[(6,0,pivline_init_ids)],
                },context=context)
        else:
            state='done'
            product_price_purs = {}
            product_price_sales = {}
            

            #Se iteran que esten pagadas o abiertas y que esten dentro del periodo al que corresponde
            #la fecha actual 
            product_price = []
            for ail_id in ail_ids:
                ail = ail_obj.browse(cr,uid,ail_id,context=context)
                
                #si la factura se relaciona a la lista de productos que se filtraron
                if ail.product_id.id in prod_ids:
                    
                    produc_obj = prod_obj.browse(cr, uid, ail.product_id.id, context=context)
                    
                    price_unit = self.exchange(cr, uid, ids, ail.price_unit, ail.invoice_id.currency_id.id, currency_id, date,context=context)

                    if ail.invoice_id.type == 'in_invoice':
                        p_p_pur = {'qty':ail.quantity,'price':price_unit}
                        if product_price_purs.get(ail.product_id.id, False):
                            product_price_purs[ail.product_id.id].append(p_p_pur)
                        else:
                            product_price_purs[ail.product_id.id] = [p_p_pur]
                    elif ail.invoice_id.type == 'out_invoice':
                        p_p_sale = {'qty':ail.quantity,'price':price_unit}
                        if product_price_sales.get(ail.product_id.id, False):
                            product_price_sales[ail.product_id.id].append(p_p_sale)
                        else:
                            product_price_sales[ail.product_id.id] = [p_p_sale]
                    else:
                        print ail.invoice_id.type
                    product_price.append(ail.product_id.id)
            
            lineas = []
            for i in prod_ids:
                
                prod = prod_obj.browse(cr,uid,i,context=context)
                val_line_ids = periodic_line.search(cr,uid,[('product_id','=',i),('piv_id','=',ids[0])],context=context)
                val_line = periodic_line.browse(cr, uid, val_line_ids, context=context)[0]
                #~~~~~~~~~~~                
                qty_pur = 0
                costo = 0.0
                qty_sale = 0
                #Si el producto fue parte de una compra
                if product_price_purs.get(i, False):
                    for j in product_price_purs[i]:
                        costo += j.get('qty')*j.get('price')
                        qty_pur += j.get('qty')

                #Si el producto fue parte de una venta
                if product_price_sales.get(i, False):
                    for k in product_price_sales[i]:
                        #inventario_final -= k.get('qty')
                        qty_sale += k.get('qty')
                inventario_final = val_line.qty_init + qty_pur - qty_sale


                costo += val_line.valuation
                qty = val_line.qty_init + qty_pur # este val_line.init es el final de la linea anterior
                
                if qty == 0:
                    costo_promedio = 0
                else:
                    costo_promedio = round(costo / qty, 2)
                
                valuation  = (val_line.valuation) + (qty_pur * costo_promedio) - (qty_sale * costo_promedio)
                # ~~~~~~~~~~~
                
                #Algo pasa con prod.property_account_expense y prod.property_account_income
                #Establezco los diarios para hacer los asientos


                #Product valuation and journal item amount
                journal_item = valuation - val_line.valuation

                debit = journal_item > 0 and journal_item or 0.0
                credit = journal_item < 0 and (journal_item*-1) or 0.0
                
                if journal_item != 0:
                    if prod.property_account_expense:
                        account_expense = prod.property_account_expense 
                    else:
                        account_expense = prod.product_tmpl_id.categ_id.property_account_expense_categ
                   
                    account_income = prod.product_tmpl_id.categ_id.property_stock_valuation_account_id
                   
                    if not account_expense or not account_income:
                        raise osv.except_osv(_('Error!'), _('Product Account.\nThere are no accounts defined for the product %s.' % (prod.name) ))


                    context['journal_id'] = inventory_valuation_journal_id
                    context['period_id'] = period_id
                    move_line = {      
                        'name': 'GANANCIA O PERDIDA DE INVENTARIO',                 
                        'partner_id': False,           
                        'product_id':prod.id,
                        'account_id': account_income.id, 
                        'move_id': False,                                             
                        'journal_id': inventory_valuation_journal_id,                               
                        'period_id': period_id,                                 
                        'date': date_stop,                               
                        'debit': debit,                                                   
                        'credit': credit,                                                  
                       }
                    
                    line_id = self.pool.get('account.move.line').create(cr, uid, move_line, context=context)
                    lineas.append(line_id)

                    move_line['account_id'] = account_expense.id 
                    move_line['debit'] = credit
                    move_line['credit'] = debit
                    
                    line_id = self.pool.get('account.move.line').create(cr, uid, move_line, context=context)
                    lineas.append(line_id)
                
                periodic_line.write(cr, uid, val_line.id, {
                    'average_cost':costo_promedio,
                    'valuation': valuation,
                    'qty_sale':qty_sale ,
                    'qty_purchase':qty_pur ,
                    'qty_final':inventario_final,
                        })
            ##############################################################
            if lineas:
                move_id = self.pool.get('account.move.line').browse(cr, uid, lineas[0], context=context).move_id.id
            else:
                move_id = False

        self.write(cr,uid,ids[0],{
            'product_ids':[(6,0,prod_ids)],
            'ail_ids':[(6,0,ail_ids)],
            'date':date or fields.date.today(),
            'stock_move_ids':[(6,0,incoming_sm_ids+outgoing_sm_ids)],
            'first':True,
            'aml_ids':[(6, 0, lineas)],
            'move_id': move_id,
            'state': state,
            },context=context)
    
        return True
    
