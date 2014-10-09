#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <humbertoarocha@gmail.com>
#    Audited by: Humberto Arocha <humbertoarocha@gmail.com>
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
from openerp.tools.translate import _


class mrp_production_workcenter_line(osv.Model):
    """ This class inherits Work Order to add two fields that are handling products
    entering and products leaving in the work order
    """
    _inherit = 'mrp.production.workcenter.line'
    _description = 'Work Order'

    _columns = {
        'mrp_workorder_variation_line_ids': fields.one2many('mrp.workorder.variation.line',
        'mrp_production_workcenter_line_id', 'Real Products Quantity'),

        'mrp_workorder_variation_output_line_ids': fields.one2many('mrp.workorder.output.variation.line',
        'mrp_production_workcenter_output_line_id', 'Real Output Products Quantity'),
    }


class mrp_workorder_variation_line(osv.Model):
    """ This class are product lines that are received in a work order
    """

    _name = 'mrp.workorder.variation.line'
    _rec_name = "product_id"

    _columns = {
        'mrp_production': fields.related('mrp_production_workcenter_line_id', 'production_id',
                                         string='Production Order', relation='mrp.production', type='many2one', store=True,
                                         help='Id Manufacturing Order'),
        'mrp_production_workcenter_line_id': fields.many2one('mrp.production.workcenter.line',
        'Production Workcenter Line ID', required=True, help='Id Work Order'),
        'product_id': fields.many2one('product.product', _('Product'), required=True,
                                      help=_('Product')),
        'product_qty': fields.float(_('Capacity'), required=True, help=_('Real Quantity')),
        'product_uom': fields.many2one('product.uom', _('Unit of Measure'), required=True,
                                       help=_('Unit of Measure')),
    }

    def on_change_product_uom(self, cr, uid, ids, product_id):
        """ Change the unit of measure depending on the product
        """
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id)
        return {'value': {'product_uom': product.uom_id and product.uom_id.id}}


class mrp_workorder_output_variation_line(osv.Model):
    """ This class are product lines that are produced in a work order
    """

    _name = 'mrp.workorder.output.variation.line'
    _rec_name = "product_id"

    _columns = {
        'mrp_production': fields.related('mrp_production_workcenter_output_line_id', 'production_id',
                                         string='Production Order', relation='mrp.production', type='many2one', store=True,
                                         help='Id Manufacturing Order'),
        'mrp_production_workcenter_output_line_id': fields.many2one('mrp.production.workcenter.line',
        'Production Workcenter Line ID', required=True, help='Id Work Order'),
        'product_id': fields.many2one('product.product', _('Product'), required=True,
                                      help=_('Product')),
        'product_qty': fields.float(_('Capacity'), required=True, help=_('Real Quantity')),
        'product_uom': fields.many2one('product.uom', _('Unit of Measure'), required=True,
                                       help=_('Unit of Measure')),
    }

    def on_change_product_uom(self, cr, uid, ids, product_id):
        """ Change the unit of measure depending on the product
        """
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id)
        return {'value': {'product_uom': product.uom_id and product.uom_id.id}}
