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


class StockConfigSettings(models.TransientModel):

    _inherit = 'stock.config.settings'

    default_location_id = fields.Many2one(
        'stock.location',
        string='Default Source Location',
        default_model='wizard.warehouse.receipt.input')

    default_location_dest_id = fields.Many2one(
        'stock.location',
        string='Default Destination Location',
        default_model='wizard.warehouse.receipt.input')
