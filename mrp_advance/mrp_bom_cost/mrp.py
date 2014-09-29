# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Coded by: rodo@vauxoo.com,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
from openerp.osv import fields, osv

import decimal_precision as dp


class mrp_bom(osv.Model):
    _inherit = 'mrp.bom'

    def _calc_cost(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = self.compute_bom_cost(cr, uid, [i.id])
        return res

    def _calc_cost_u(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para el calculo del costo unitario, el cual es:
        product cost/ product qty
        @cost = se almacena el costo unitario final.
        @res = diccionario usado para retornar el id y el costo unitario.
        '''
        res = {}
        for i in self.browse(cr, uid, ids):
            cost = 0.00
            cost = i.cost_t/i.product_qty
            for l in i.bom_lines:
                if not l.bom_lines:
                    cost = l.product_id.standard_price*l.product_qty
                    res[i.id] = cost
                else:
                    cost = cost + self._calc_cost_u(cr, uid, [l.id],
                                                field_name, arg,
                                                context)[l.id]*l.product_qty
                    res[i.id] = cost/l.product_qty
            res[i.id] = i.cost_t/i.product_qty
            if 'sub_products' in i._columns and i.sub_products:
                sum_amount_subproducts = 0.0
                product_uom_obj = self.pool.get('product.uom')
                for sub_prod in i.sub_products:
                    sum_amount_subproducts += (product_uom_obj._compute_price(
                        cr, uid, sub_prod.product_id.uom_id.id,
                        sub_prod.product_id.standard_price,
                        sub_prod.product_uom.id) * sub_prod.product_qty)
                res[i.id] =  (i.cost_t - sum_amount_subproducts) / \
                    i.product_qty  # mrp.bom valida cantidades mayores a 0
        return res

    def _get_category(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para obtener la categoria del producto y luego aplicarla
        para la filtracion
        de las categorias de los campos product_uom  y product_uos
        '''
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = (i.product_id.uom_id.category_id.id,
                         i.product_id.uom_id.category_id.name)
        return res

    def _get_category_prod(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para obtener la categoria del producto
        '''
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = (i.product_id.product_tmpl_id.categ_id.id,
                         i.product_id.product_tmpl_id.categ_id.name)
        return res

    _columns = {
        'cost_t': fields.function(_calc_cost, method=True, type='float',
            digits_compute=dp.get_precision('Cost_Bom'),
            string='Cost', store=False),
        'cost_u': fields.function(_calc_cost_u, method=True, type='float',
            digits_compute=dp.get_precision('Cost_Bom'),
            string='Unit Cost', store=False),
        'category_id': fields.function(_get_category, method=True,
            type='many2one', relation='product.uom.categ',
            string='Category Uom'),
        'category_prod_id': fields.function(_get_category_prod, method=True,
            type='many2one', relation='product.category', string='Category'),
        'product_uom_default_id': fields.related('product_id', 'uom_id',
            string="Uom Default", type='many2one', relation='product.uom'),
        #~ 'bom_assets':fields.boolean('Assets', help="Determine if the bom is of type assets."),
    }

    def compute_bom_cost(self, cr, uid, ids, *args):
        for i in self.browse(cr, uid, ids):
            cost = 0.00
            if i.bom_lines:
                for l in i.bom_lines:
                    cost += self.compute_bom_cost(cr, uid, [l.id])
            else:
                cost = i.product_id.standard_price*i.product_qty * \
                    i.product_uom.factor_inv * i.product_id.uom_id.factor

            if i.routing_id:
                for j in i.routing_id.workcenter_lines:
                    cost += j.costo_total

        return cost
