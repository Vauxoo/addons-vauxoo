# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

from openerp import models, fields


class StockMove(models.Model):

    _inherit = 'stock.move'

    warehouse_receipt_id = fields.Many2one(
        'warehouse.receipt', 'Warehouse Receipt',
        help='Is the package number which the courier manage the goods sent'
             ' to final customer. Each warehouse receipt can contain several'
             ' items from several orders too')

    purchase_order_id = fields.Many2one(
        related="purchase_line_id.order_id", store=True,
        string='Purchase Order',
    )
