# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral <kathy@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp.osv import osv, fields


class mrp_workcenter(osv.Model):

    _inherit = 'mrp.workcenter'
    _columns = {
        'product_capacity_ids': fields.one2many(
            'mrp.workcenter.product.capacity',
            'workcenter_id',
            'Products Maxime Capacity',
            help='Workcenter capacities by product'),
    }


class mrp_routing_workcenter(osv.Model):

    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'product_ids': fields.one2many(
            'mrp.workcenter.operation.product.quantity',
            'operation_id',
            'Products Needed',
            help='Products needed to the operation'),
    }


class mrp_workcenter_product_capacity(osv.Model):

    _name = 'mrp.workcenter.product.capacity'
    _description = 'Workcenter Product Capacity'

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'WorkCenter',
            required=True,
            help='Work Center'),
        'product_id': fields.many2one(
            'product.product',
            'Product',
            required=True,
            help='Product'),
        'qty': fields.float(
            'Capacity',
            required=True,
            help='Quantity'),
        'uom_id': fields.many2one(
            'product.uom',
            'Unit of Measure',
            required=True,
            help='Unit of Measure'),
    }

    _sql_constraints = [
        ('operation_prodct_uniq', 'unique (workcenter_id,product_id)',
         'Error! There is already defined capacity for this product in the '
         'current workcenter.')
    ]


class mrp_workcenter_operation_product_quantity(osv.Model):

    _name = 'mrp.workcenter.operation.product.quantity'
    _description = 'Work Center Operation Product Quantity'

    _columns = {
        'operation_id': fields.many2one(
            'mrp.routing.workcenter',
            'Operation',
            required=True,
            help='Operation'),
        'product_id': fields.many2one(
            'product.product',
            'Product',
            required=True,
            help='Product'),
        'qty': fields.float(
            'Capacity',
            required=True,
            help='Quantity'),
        'uom_id': fields.many2one(
            'product.uom',
            'Unit of Measure',
            required=True,
            help='Unit of Measure'),
    }

    _sql_constraints = [
        ('operation_prodct_uniq', 'unique (operation_id,product_id)',
         'Error! There is already defined capacity for this product in the '
         'current operation.')
    ]
