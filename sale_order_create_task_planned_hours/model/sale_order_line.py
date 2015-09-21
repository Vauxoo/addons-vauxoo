# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp import models, fields


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    estimated_hours = fields.Float(
        help="Estimated Hours taken for service "
        "If the product type is diferent to Service"
        "you can not fill the field",
        default=1.0)
    product_type = fields.Selection(related="product_id.type", store=False)
