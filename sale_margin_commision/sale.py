# coding: utf-8
from openerp.osv import fields, osv


class SaleOrder(osv.Model):

    """sale_order
    """

    def _get_commision(self, price, cost):
        return (price and cost) and ((price - cost / price) * 100) or 0

    def _check_commision(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for i in ids:
            print i
            result[i] = 10
        return result

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids,
                                                             pricelist,
                                                             product, qty=qty,
                                                             uom=uom,
                                                             qty_uos=qty_uos,
                                                             uos=uos,
                                                             name=name,
                                                             partner_id=partner_id,
                                                             lang=lang,
                                                             update_tax=update_tax,
                                                             date_order=date_order,
                                                             packaging=packaging,
                                                             fiscal_position=fiscal_position,
                                                             flag=flag)
        frm_cur = self.pool.get('res.users').browse(
            cr, uid, uid).company_id.currency_id.id
        to_cur = self.pool.get('res.partner').browse(
            cr, uid, partner_id).property_product_pricelist.currency_id.id
        if product:
            purchase_price = self.pool.get('product.product').browse(
                cr, uid, product).standard_price
            price = self.pool.get('res.currency').compute(
                cr, uid, frm_cur, to_cur, purchase_price, round=False)
            res['value'].update({'purchase_price': price})
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                if line.purchase_price:
                    res[line.id] = round((line.price_unit *
                                          line.product_uos_qty *
                                          (100.0 - line.discount) / 100.0) -
                                         (line.purchase_price *
                                          line.product_uos_qty), 2)
                else:
                    res[line.id] = round((line.price_unit * line.product_uos_qty
                                          * (100.0 - line.discount) / 100.0) -
                                         (line.product_id.standard_price *
                                          line.product_uos_qty), 2)
        return res

    _inherit = 'sale.order'
    _columns = {
        'commision': fields.function(_check_commision, method=True,
                                     type='float', string='Commision Rate',
                                     store=True,
                                     help="""It is the commision calculate
                                              based on baremos"""),
        'margin': fields.function(_check_commision, method=True,
                                  type='float', string='Margin', store=True,
                                  help="""It gives profitability by
                                          calculating the difference between
                                          the Unit Price and Cost Price."""),
    }
