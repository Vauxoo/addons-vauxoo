# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Revision: --- nhomar.hernandez@netquatro.com
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
import time
import netsvc
import ir
from mx import DateTime
import pooler

class purchase_order_line(osv.osv):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, line.price_unit * line.product_qty )
        return res

    _columns = {
        'discount': fields.float('Discount (%)', digits=(16,2), help="If you chose apply a discount for this way you will overide the option of calculate based on Price Lists, you will need to change again the product to update based on pricelists, this value must be between 0-100"),
        'price_unit': fields.float('Real Unit Price', required=True, digits=(16, 4), help="Price that will be used in the rest of accounting cycle"),
        'price_base': fields.float('Base Unit Price', required=True, digits=(16, 4), help="Price base taken to calc the discount, is an informative price to use it in the rest of the purchase cycle like reference for users"),
    }
    _defaults = {
        'discount': lambda *a: 0.0,
    }

    def discount_change(self, cr, uid, ids, product, discount, price_unit, product_qty, partner_id, price_base):
        if not product:
            return {'value': {'price_unit': 0.0,}}
        prod= self.pool.get('product.product').browse(cr, uid,product)
        lang=False
        res=[]
        #TODO Improve pending to offer discounts based in price lists selected on order.
        if res==[]:
            res = {'value': {'price_unit': price_base*(1-discount/100),'price_base': price_base}}
            return res

    def rpu_change(self, cr, uid, ids, rpu, discount):
        res = {'value': {'price_base': rpu*(1+discount/100)}}
        return res

    def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position=False):
        """Copied from purchase/purchase.py and modified to take discount"""
        if not pricelist:
            raise osv.except_osv(_('No Pricelist !'), _('You have to select a pricelist in the purchase form !\nPlease set one before choosing a product.'))
        if not  partner_id:
            raise osv.except_osv(_('No Partner!'), _('You have to select a partner in the purchase form !\nPlease set one partner before choosing a product.'))
        if not product:
            return {'value': {'price_unit': 0.0, 'name':'','notes':'', 'product_uom' : False}, 'domain':{'product_uom':[]}}
        prod= self.pool.get('product.product').browse(cr, uid,product)
        lang=False
        if partner_id:
            lang=self.pool.get('res.partner').read(cr, uid, partner_id)['lang']
        context={'lang':lang}
        context['partner_id'] = partner_id

        prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
        prod_uom_po = prod.uom_po_id.id
        if not uom:
            uom = prod_uom_po
        if not date_order:
            date_order = time.strftime('%Y-%m-%d')

        qty = qty or 1.0
        seller_delay = 0
        for s in prod.seller_ids:
            if s.name.id == partner_id:
                seller_delay = s.delay
                temp_qty = s.qty # supplier _qty assigned to temp
                if qty < temp_qty: # If the supplier quantity is greater than entered from user, set minimal.
                    qty = temp_qty

        price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom,
                    'date': date_order,
                    })[pricelist]
        dt = (DateTime.now() + DateTime.RelativeDateTime(days=int(seller_delay) or 0.0)).strftime('%Y-%m-%d %H:%M:%S')
        prod_name = prod.partner_ref


        res = {'value': {'price_unit': price, 'price_base': price, 'name':prod_name, 'taxes_id':map(lambda x: x.id, prod.supplier_taxes_id),
            'date_planned': dt,'notes':prod.description_purchase,
            'product_qty': qty,
            'product_uom': uom}}
        domain = {}

        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        taxes = self.pool.get('account.tax').browse(cr, uid,map(lambda x: x.id, prod.supplier_taxes_id))
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        res['value']['taxes_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)

        res2 = self.pool.get('product.uom').read(cr, uid, [uom], ['category_id'])
        res3 = prod.uom_id.category_id.id
        domain = {'product_uom':[('category_id','=',res2[0]['category_id'][0])]}
        if res2[0]['category_id'][0] != res3:
            raise osv.except_osv(_('Wrong Product UOM !'), _('You have to select a product UOM in the same category than the purchase UOM of the product'))

        res['domain'] = domain
        return res

purchase_order_line()

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def _get_order(self, cr, uid, ids, context={}):
        """Copied from purchase/purchase.py"""
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def inv_line_create(self, cr, uid, a, ol):
        res = super(purchase_order,self).inv_line_create(cr, uid, a, ol)
        res[2].update({'discount': ol.discount, 'price_unit': ol.price_base or 0.0,})
        return res

purchase_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_discount_invoice(self, cursor, user, move_line):
        '''Return the discount for the move line'''
        discount = 0.00
        if move_line and move_line.purchase_line_id:
            discount = move_line.purchase_line_id.discount
        return discount

stock_picking()

class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'

    def _get_price_wd(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            if line.invoice_id:
                res[line.id] = line.price_unit * (1-(line.discount or 0.0)/100.0)
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
            else:
                res[line.id] = line.price_unit * (1-(line.discount or 0.0)/100.0)
        return res

    _columns={
    'price_wd': fields.function(_get_price_wd, method=True, string='Price With Discount',store=True, type="float", digits=(16, 4)),
    }
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
