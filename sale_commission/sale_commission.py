# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp


class sale_commission(osv.Model):

    def _get_commission(self, cr, uid, ids, name, args, context=None):
        res = {}

        for so_brw in self.browse(cr, uid, ids):
            res[so_brw.id] = 0.0
            for sol_brw in so_brw.order_line:
                res[so_brw.id] += sol_brw.commission
        return res

    def _get_order_line(self, cr, uid, ids, context=None):
        res = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            res[line.order_id.id] = True
        return res.keys()

    _inherit = 'sale.order'
    _columns = {
        'commission': fields.function(_get_commission, method=True, type='float', string='Commission', digits_compute=dp.get_precision('Commission'),
                                      store={
                                      'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'state'], 25),
                                      'sale.order.line': (_get_order_line, ['gain', 'commission'], 15), })
    }


class sale_commission_line(osv.Model):

    def get_abs_commission(self, cr, uid, ids, name, args, context=None):

        bar_obj = self.pool.get('baremo.book')
        res = {}
        for sol_brw in self.browse(cr, uid, ids):
            bar_id = hasattr(sol_brw.company_id,'bar_id') and sol_brw.company_id.bar_id  and sol_brw.company_id.bar_id.id or False
            print '--------------- bar_id -------------', bar_id
            if not bar_id:
                # TODO: raise exception, levantar excepcion.
                # de momento esta asi como se muestra, enviando
                # un calculo igual a cero para cuando no haya
                # establecido en la company un tipo de baremo
                print 'NO HAY BAREMO EN LA COMPANY'
                res[sol_brw.id] = 0.0
                continue
            rate = sol_brw.gain
            rate_comm = bar_obj._calc_comm(
                cr, uid, ids, bar_id, rate, 0.0, context=None)['rate_comm']
            res[sol_brw.id] = sol_brw.price_subtotal * rate_comm / 100
            print 'res[%s] = subtotal(%s) * tasa(%s) => %s' % (sol_brw.id, sol_brw.price_subtotal, rate_comm, res[sol_brw.id])
        return res

    def get_gain(self, cr, uid, ids, name, args, context=None):
        res = {}
        product_price = 0
        product_pu = 0
        gain = 0
        for sol_brw in self.browse(cr, uid, ids):
            if sol_brw.product_id:
                product_cost = sol_brw.product_id.standard_price
                if product_cost != 0.0:
                    product_pu = sol_brw.price_unit
                    res[sol_brw.id] = ((
                        product_pu-product_cost)/product_cost)*100
                else:
                    raise osv.except_osv(_("User Error"), _(
                        "The product standard price can't be 0.0!"))
            else:
                res[sol_brw.id] = 0.0
        print 'get_gain'
        return res

    _inherit = 'sale.order.line'
    _columns = {
        'gain': fields.function(get_gain, method=True, type='float', string='Gain', digits_compute=dp.get_precision('Commission'),
                                store={
                                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'price_subtotal', 'product_uom_qty'], 15),
                                }),
        'commission': fields.function(get_abs_commission, method=True, type='float', string='Commission', digits_compute=dp.get_precision('Commission'),
                                      store={
                                      'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, None, 25),
                                      }),
    }

