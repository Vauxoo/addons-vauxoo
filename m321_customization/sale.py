# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Luis Escobar  <p.com.ve>
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
import decimal_precision as dp
import netsvc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class inherited_sale_order(osv.osv):
    _inherit = "sale.order"

    def price_unit_confirm(self,cr,uid,ids,context=None):
        '''
        Workflow condition does not allow the sale process if at least one
        product is being sold in the price range set out in its cost structure
        '''
        if context is None:
            context = {}
        for sale in len(ids) == 1 and self.browse(cr, uid, ids, context=context) or []:
            if sale.pass_sale:
                return True

            else:
                res = super(inherited_sale_order, self).price_unit_confirm(cr, uid, ids, context=context)
                return res     


    _columns = {
            'pass_sale': fields.boolean('Validate', help='If this field is true the sale is validate without validate price'), 
            
            }

    
    def action_ship_create(self, cr, uid, ids, *args):
        wf_service = netsvc.LocalService("workflow")
        picking_id = False
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context={}):
            proc_ids = []
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            picking_id = False
            for line in order.order_line:
                proc_id = False
                date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')

                if line.state == 'done':
                    continue
                move_id = False
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    if not picking_id:
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'name': pick_name,
                            'origin': order.name,
                            'type': 'out',
                            'state': 'auto',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                            'company_id': order.company_id.id,
                        })
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': line.name[:64],
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'percent_com': line.percent_com,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos_qty,
                        'product_uos': (line.product_uos and line.product_uos.id)\
                                or line.product_uom.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'draft',
                        #'state': 'waiting',
                        'note': line.notes,
                        'company_id': order.company_id.id,
                    })

                if line.product_id:
                    proc_id = self.pool.get('procurement.order').create(cr, uid, {
                        'name': line.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': (line.product_uos and line.product_uos_qty)\
                                or line.product_uom_qty,
                        'product_uos': (line.product_uos and line.product_uos.id)\
                                or line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                        'move_id': move_id,
                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],
                        'company_id': order.company_id.id,
                    })
                    proc_ids.append(proc_id)
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
                    if order.state == 'shipping_except':
                        for pick in order.picking_ids:
                            for move in pick.move_lines:
                                if move.state == 'cancel':
                                    mov_ids = move_obj.search(cr, uid, [('state', '=', 'cancel'),('sale_line_id', '=', line.id),('picking_id', '=', pick.id)])
                                    if mov_ids:
                                        for mov in move_obj.browse(cr, uid, mov_ids):
                                            move_obj.write(cr, uid, [move_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})
                                            proc_obj.write(cr, uid, [proc_id], {'product_qty': mov.product_qty, 'product_uos_qty': mov.product_uos_qty})

            val = {}

            if picking_id:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

            for proc_id in proc_ids:
                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

            if order.state == 'shipping_except':
                val['state'] = 'progress'
                val['shipped'] = False

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
            self.write(cr, uid, [order.id], val)
        return True

    
    def default_get(self, cr, uid, fields, context=None):
        """
             To get default values for the object.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param fields: List of fields for which we want default values
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        res = super(inherited_sale_order, self).default_get(cr, uid, fields, context=context)
        res.get('order_policy',False) and res.update({'order_policy':'picking'})
        return res

    
    _defaults = {
        'order_policy': 'picking',
        'pass_sale':False,
    }
    
    def qty_confirm(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        product = []
        sale_brw = ids and self.browse(cr,uid,ids[0],context=context)
        for line in sale_brw.order_line:
            virtual = line.product_id.qty_available
            real = line.product_id.virtual_available
            if virtual == real and line.product_uom_qty > virtual or line.product_uom_qty > virtual:
                raise osv.except_osv(_('Error'), _('The quantity in the line of the product %s is minor that quantity available '%line.product_id.name))
            
            elif virtual > real and line.product_uom_qty > real and line.product_uom_qty < virtual and not line.check_confirm:
                raise osv.except_osv(_('Error'), _('The amount you want to sell is not available in the real stock of product %s, but if a shipment next, if you want to make this sale select Stock future sales line'%line.product_id.name))
                
        return True
    
    
    
inherited_sale_order()


class sale_order_line(osv.osv):
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context=None):
        if context is None:
            context ={}
        product_obj = self.pool.get('product.product')
        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)
        
        future_stock = product and self.pool.get('stock.move').search(cr,uid,[('product_id','=',product),
                                                                              ('state','in',('assigned','confirmed','waiting')),
                                                                              ('picking_id.type','=','in')],context=context)
        future_stock and res.get('value',False) and res.get('value',False).update({'stock_move_ids':future_stock })
        
        return res
    
    def price_unit(self,cr,uid,ids,price_list,product_id,qty,context=None):
        '''
        Calculating the amount of model _compute_price method product.uom
        '''
        if context is None:
            context = {}
        res = super(sale_order_line,self).price_unit(cr,uid,ids,price_list,product_id,qty,context) 
        if price_list:
            price_obj = self.pool.get('product.pricelist')
            price = price_obj.browse(cr, uid, price_list, context=context)
            percen = price.percent_com
            res.get('value',{}).update({'percent_com':percen})
        return res
   

    _inherit = 'sale.order.line'
    _columns = {
        'stock_move_ids':fields.one2many('stock.move','id_sale','Future Stock',readonly=True,help="Stock move future to reference of salesman for knowing that product is available"),
        'check_confirm':fields.boolean("Future Stock'",help="This field indicates if the salesman is in accordance with sale a product   that is not available but if in a future stock"),
    'percent_com':fields.float('Percen Commision', help='Percent commision by price list'), 
    
    }
   
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(cr, uid,
                        line.procurement_id.id, context=context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(cr, uid,
                        line.procurement_id.id, context=context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    a = prop and prop.id or False
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                if not a:
                    raise osv.except_osv(_('Error !'),
                                _('There is no income category account defined in default Properties for Product Category or Fiscal Position is not defined !'))
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'price_unit': pu,
                    'percent_com': line.percent_com,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                    'note': line.notes,
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})
                sales[line.order_id.id] = True
                create_ids.append(inv_id)
        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids



sale_order_line()

