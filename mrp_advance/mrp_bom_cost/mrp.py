# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
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
from osv import osv
from osv import fields
from tools.translate import _

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def _calc_cost(self, cr, uid, ids, field_name, arg, context):
        res={}
        for i in self.browse(cr,uid,ids):
            res[i.id] = self.compute_bom_cost(cr, uid, [i.id])
        return res

    def _calc_cost_u(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para el calculo del costo unitario, el cual es: product cost/ product qty
        @cost = se almacena el costo unitario final.
        @res = diccionario usado para retornar el id y el costo unitario.
        '''
        res={}
        for i in self.browse(cr,uid,ids):
            cost = 0.00
            cost = i.cost_t/i.product_qty
            for l in i.bom_lines:
                if not l.bom_lines:
                    cost =  l.product_id.standard_price*l.product_qty
                    res[i.id]= cost
                else:
                    cost = cost + self._calc_cost_u(cr,uid,[l.id],field_name,arg,context)[l.id]*l.product_qty
                    res[i.id]=cost/l.product_qty
            res[i.id] = i.cost_t/i.product_qty
        return res

    def _get_category(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para obtener la categoria del producto y luego aplicarla para la filtracion
        de las categorias de los campos product_uom  y product_uos
        '''
        res={}
        for i in self.browse(cr,uid,ids):
            res[i.id] = (i.product_id.uom_id.category_id.id,i.product_id.uom_id.category_id.name)
        return res

    _columns = {
        'cost_t': fields.function(_calc_cost, method=True, type='float', string='Cost', store=False),
        'cost_u': fields.function(_calc_cost_u, method=True, type='float', string='Unit Cost', store=False),
        'category_id': fields.function(_get_category, method=True, type='many2one',relation='product.uom.categ'),
        #~ 'bom_assets':fields.boolean('Assets', help="Determine if the bom is of type assets."),
    }
    

    def compute_bom_cost(self, cr, uid, ids, *args):
        for i in self.browse(cr,uid,ids):
            cost = 0.00
            if i.bom_lines:
                for l in i.bom_lines:
                    cost += self.compute_bom_cost(cr, uid, [l.id])
            else:
                cost = i.product_id.standard_price*i.product_qty* i.product_uom.factor_inv * i.product_id.uom_id.factor
                
            if i.routing_id:
                for j in i.routing_id.workcenter_lines:
                    cost += j.costo_total
                
        return cost
    
mrp_bom()

