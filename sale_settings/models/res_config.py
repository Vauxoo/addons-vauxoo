# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded /planned by: Katherine Zaoral <kathy@vauxoo.com>
############################################################################

from openerp import fields, models


class SaleConfiguration(models.TransientModel):

    _inherit = 'sale.config.settings'

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self:
        self.env['res.company']._company_default_get('sale.config.settings'))
