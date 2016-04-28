# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Hugo Adan, <hugo@vauxoo.com>
############################################################################
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    check_invoice = fields.Boolean(
        readonly=True, default=False,
        help="Check Invoices vs Pickings in all Customers transfers")
