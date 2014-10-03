# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
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
from openerp.addons.decimal_precision import decimal_precision as dp


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'variation_ids': [],
            'variation_finished_product_ids': [],
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)

    _columns = {
        'variation_ids': fields.one2many('mrp.variation', 'production_id',
            'Variation Product Consumed', readonly=True),
        'variation_finished_product_ids': fields.one2many(
            'mrp.variation.finished.product', 'production_id',
            'Variation Product Finished', readonly=True),
    }

    def action_finish(self, cr, uid, ids, context={}):
        res = super(mrp_production, self).action_finish(
            cr, uid, ids, context=context)
        self.create_variation_consumed(cr, uid, ids, context=context)
        self.create_variation_finished_product(cr, uid, ids, context=context)
        return res

    def create_variation(self, cr, uid, ids, real={}, planned={}, context={}):
        prod_product = self.pool.get('product.product')
        list_val = []
        for production in self.browse(cr, uid, ids, context=context):
            lista = []
            lista.extend(real.keys())
            lista.extend(planned.keys())
            lista = list(set(lista))
            res_diff = dict(planned)
            for product_id in lista:
                res_diff.setdefault(product_id, 0)
                res_diff[product_id] -= real.get(product_id, 0)
            for val_diff in res_diff.items():
                val = {'product_id': val_diff[0],
                       'quantity': (val_diff[1])*-1,
                       'product_uom': prod_product.browse(cr, uid,
                                        val_diff[0]).uom_id.id,
                       'production_id': production.id
                       }
                list_val.append(val)
        return list_val

    def create_res_real_planned(self, cr, uid, dat=False):
        product_product = self.pool.get('product.product')
        if dat is False:
            dat = []
        res = {}
        for lin in dat:
            res.setdefault(lin['product_id'], 0)
            product = product_product.browse(cr, uid, lin['product_id'])
            qty_uom_convert = self.pool.get('product.uom')._compute_qty(cr,
                                uid, lin['product_uom'], lin['product_qty'],
                                to_uom_id=product.uom_id.id)
            res[lin['product_id']] += qty_uom_convert
        return res

    def create_consume_real(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                    SELECT sm.product_uom,sm.product_id,
                        sum(COALESCE(sm.product_qty,0)) AS product_qty
                        FROM mrp_production_move_ids mpmi JOIN stock_move sm
                        ON sm.id=mpmi.move_id
                    WHERE mpmi.production_id=%s
                    AND sm.state='done'
                    GROUP BY sm.product_id,sm.product_uom
                    """, (production.id,))
            dat = cr.dictfetchall()
            res_real = self.create_res_real_planned(cr, uid, dat)
        return res_real

    def create_consume_planned(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                    SELECT product_id,sum(COALESCE(product_qty,0))
                        AS product_qty,product_uom
                        FROM mrp_production_product_line
                    WHERE production_id=%s
                    GROUP BY product_id,product_uom
                    """, (production.id,))
            dat = cr.dictfetchall()
            res_planned = self.create_res_real_planned(cr, uid, dat)
        return res_planned

    def create_finished_product_real(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                    SELECT product_id,product_uom,sum(product_qty)
                        AS product_qty
                        FROM stock_move
                    WHERE production_id=%s
                    AND state='done'
                    GROUP BY product_id,product_uom
                    """, (production.id,))
            dat = cr.dictfetchall()
            res_real = self.create_res_real_planned(cr, uid, dat)
        return res_real

    def create_finished_product_planned(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                    SELECT product_id,sum(quantity) AS product_qty, product_uom
                        FROM mrp_pt_planified
                    WHERE production_id=%s
                    GROUP BY product_id,product_uom
                    """, (production.id,))
            dat = cr.dictfetchall()
            res_planned = self.create_res_real_planned(cr, uid, dat)
        return res_planned

    def create_variation_consumed(self, cr, uid, ids, context={}):
        prod_variation_consumed = self.pool.get('mrp.variation')
        for production in self.browse(cr, uid, ids, context=context):
            prod_variation_consumed.unlink(cr, uid, map(
                lambda x: x.id, production.variation_ids))
            real = self.create_consume_real(cr, uid, ids, context=context)
            planned = self.create_consume_planned(
                cr, uid, ids, context=context)
            res = self.create_variation(
                cr, uid, ids, real, planned, context=context)
            [prod_variation_consumed.create(cr, uid, lin) for lin in res]
        return True

    def create_variation_finished_product(self, cr, uid, ids, context={}):
        prod_variation_finished_product = self.pool.get(
            'mrp.variation.finished.product')
        for production in self.browse(cr, uid, ids, context=context):
            prod_variation_finished_product.unlink(cr, uid, map(
                lambda x: x.id, production.variation_finished_product_ids))
            real = self.create_finished_product_real(
                cr, uid, ids, context=context)
            planned = self.create_finished_product_planned(
                cr, uid, ids, context=context)
            res = self.create_variation(
                cr, uid, ids, real, planned, context=context)
            [prod_variation_finished_product.create(
                cr, uid, lin) for lin in res]
        return True


class mrp_variation(osv.Model):
    _name = 'mrp.variation'
    _rec_name = 'product_id'

    def _get_variation_cost(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for variation in self.browse(cr, uid, ids, context=context):
            res[variation.id] = variation.quantity * \
                variation.product_id.standard_price
        return res

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'quantity': fields.float('Quantity',
            digits_compute=dp.get_precision('Product UoM')),
        'production_id': fields.many2one('mrp.production', 'production'),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'cost_variation': fields.function(_get_variation_cost, type='float',
            digits_compute=dp.get_precision('Purchase Price'),
            string='Variation Cost')
    }


class mrp_variation_finished_product(osv.Model):
    _name = 'mrp.variation.finished.product'
    _rec_name = 'product_id'

    def _get_variation_cost(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for variation in self.browse(cr, uid, ids, context=context):
            res[variation.id] = variation.quantity * \
                variation.product_id.standard_price
        return res

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'quantity': fields.float('Quantity',
            digits_compute=dp.get_precision('Product UoM')),
        'production_id': fields.many2one('mrp.production', 'production'),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'cost_variation': fields.function(_get_variation_cost, type='float',
            digits_compute=dp.get_precision('Purchase Price'),
            string='Variation Cost')
    }
