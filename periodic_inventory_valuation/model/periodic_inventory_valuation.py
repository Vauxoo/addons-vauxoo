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

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
            'journal_id': fields.many2one('account.journal', 'Periodical Inventory Valuation Journal', help="Journal entry"),
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
        'journal_id':fields.many2one('account.journal', 'Journal', help='Accounting Journal to be used when creating Journal Entries and Accounting Entries'),         
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
        }

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
        period_ids = period_obj.find(cr,uid,dt=date,context=context)
        print "periods ids" , period_ids, " date ", date, ' company_id' , piv_brw.company_id.id
        period_ids = period_obj.search(cr,uid,[
            ('id','in',period_ids),('special','=',False)],context=context)
        period_ids = period_ids and period_ids[0] or False
        if not period_ids:
            raise osv.except_osv(_('Error!'), _('There is no fiscal year defined for this date.\nPlease create one from the configu     ration of the accounting menu.'))


        inv_obj = self.pool.get('account.invoice')
        inv_ids = inv_obj.search(cr,uid,[
            ('state','in',('open','paid')),('period_id','=',period_ids),
            ('company_id','=',company_id)
            ],context=context)
        print "facturas", inv_ids
        if not inv_ids:
            raise osv.except_osv(_('Error!'), _('There are no invoices defined for this period.\nMake sure you are using the right date.'))
        ail_obj = self.pool.get('account.invoice.line')
        ail_ids = ail_obj.search(cr,uid,[
            ('invoice_id','in',inv_ids),('product_id','in',prod_ids)
            ],context=context)
        if not ail_ids:
            raise osv.except_osv(_('Error!'), _('There are no invoices lines defined for this period.\nMake sure you are using the right date.'))

        period_brw = period_obj.browse(cr,uid,period_ids,context=context)
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

        periodic_line = self.pool.get('periodic.inventory.valuation.line')
        if not self.browse(cr,uid,ids[0],context=context).first:
            pivl_init_ids = []
            for prod_id in prod_ids:
                prod = prod_obj.browse(cr,uid,prod_id,context=context)
                pivl_init_ids.append(periodic_line.create(cr, uid, {
                        'piv_id': ids[0],
                        'product_id':prod_id,
                        'qty_init':0.0,
                        'qty_final':1.0,
                        'qty_sale':0.0,
                        'qty_purchase':1.0,
                        'uom_id':prod.uom_id.id,
                        'average_cost':40.0,
                        'valuation':40.0,
                        }, context=context))

            self.write(cr,uid,ids[0],{
                'pivl_ids':[(6,0,pivl_init_ids)],
                },context=context)
        else:
            product_price_purs = {}
            product_price_sales = {}
            qty_purchase = 0 
            total_purchase = 0 
            for ail_id in ail_ids:
                ail = ail_obj.browse(cr,uid,ail_id,context=context)
                if ail.product_id.id in prod_ids:
                    
                    produc_obj = prod_obj.browse(cr, uid, ail.product_id.id, context=context)
                    #new_valuation = val_line.valuation
                    #new_cost_prom = 0
                    #new_cost_prom = ( val_line.average_cost + (product_obj. * ail.quantity) ) / ( (qty_purchase - qty_sale) + val_line.qty_init )
                    
                    #en otro ciclo

                    if ail.invoice_id.type == 'in_invoice':
                        p_p_pur = {'qty':ail.quantity,'price':ail.price_unit}
                        if product_price_purs.get(ail.product_id.id, False):
                            product_price_purs[ail.product_id.id].append(p_p_pur)
                        else:
                            product_price_purs[ail.product_id.id] = [p_p_pur]
                    elif ail.invoice_id.type == 'out_invoice':
                        p_p_sale = {'qty':ail.quantity,'price':ail.price_unit}
                        if product_price_sales.get(ail.product_id.id, False):
                            product_price_sales[ail.product_id.id].append(p_p_sale)
                        else:
                            product_price_sales[ail.product_id.id] = [p_p_sale]
                    else:
                        print ail.invoice_id.type
            
            for i in product_price_purs:
                qty_pur = 0
                costo = 0.0
                if product_price_purs.get(i, False):
                    for j in product_price_purs[i]:
                        costo += j.get('qty')*j.get('price')
                        qty_pur += j.get('qty')
                    
                    val_line_ids = periodic_line.search(cr,uid,[('product_id','=',i)],context=context)
                    val_line = periodic_line.browse(cr, uid, val_line_ids, context=context)[0]
                    
                    costo += val_line.qty_final * val_line.average_cost
                    
                    qty = qty_pur + val_line.qty_final
                    costo_promedio = round(costo / qty, 2)
                    
                    print 'costo bienes disponibles' , costo, ' cantidad disponible ' , qty , ' costo_promedio por unidad ', costo_promedio
                    
                    inventario_final = qty
                    if product_price_sales.get(i, False):
                        for k in product_price_sales[i]:
                            inventario_final -= k.get('qty')
                    
                    print 'qty compras - qty ventas (inventario final)' , inventario_final
                    print 'inventario_final * costo_promedio' , inventario_final * costo_promedio
                    print '\n\n'
#DUDA con VALUATION
                periodic_line.write(cr, uid, val_line.id, {
                    'average_cost':costo_promedio,
                    'valuation':costo - (inventario_final * costo_promedio),
                    'qty_sale':qty - inventario_final ,
                    'qty_purchase':qty_pur ,
                    'qty_final':inventario_final,
                    'qty_init':val_line.qty_final,
                        })
            
            
            print "products_price_pur " , product_price_purs , " products_price_sale " , product_price_sales
            print "qty_purchase " , qty_purchase , " total_purchase " , total_purchase
                    
        self.write(cr,uid,ids[0],{
            'product_ids':[(6,0,prod_ids)],
            'ail_ids':[(6,0,ail_ids)],
            'period_id':period_ids,
            'date':date or fields.date.today(),
            'stock_move_ids':[(6,0,incoming_sm_ids+outgoing_sm_ids)],
            'first':True,
            },context=context)
    
        return True
    
