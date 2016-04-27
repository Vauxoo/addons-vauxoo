# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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


class MrpSubproduct(osv.Model):
    _inherit = 'mrp.subproduct'

    def _calc_cost(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in self.browse(cr, uid, ids):
            res[i.id] = self.compute_bom_cost(cr, uid, [i.id])
        return res

    def _calc_cost_u(self, cr, uid, ids, field_name, arg, context):
        """funcion para el calculo del costo unitario, el cual es: product cost/ product qty
        @cost = se almacena el costo unitario final.
        @res = diccionario usado para retornar el id y el costo unitario.
        """
        res = {}
        for i in self.browse(cr, uid, ids):
            cost = 0.00
            cost = i.product_id.standard_price
            res[i.id] = cost
        return res

    _columns = {
        'cost_t': fields.function(_calc_cost, method=True, type='float', digits_compute=dp.get_precision('Cost_Bom'), string='Cost', store=False),
        'cost_u': fields.function(_calc_cost_u, method=True, type='float', digits_compute=dp.get_precision('Cost_Bom'), string='Unit Cost', store=False),
    }

    def compute_bom_cost(self, cr, uid, ids, *args):
        for i in self.browse(cr, uid, ids):
            cost = 0.00
            cost = i.product_id.standard_price * i.product_qty * \
                i.product_uom.factor_inv * i.product_id.uom_id.factor

        return cost
