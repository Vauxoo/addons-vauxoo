# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re
from openerp import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(copy=False)
    commercial_vat = fields.Char(compute='_compute_commercial_vat',
                                 store=True,
                                 help='Vat unique for global partner')

    @api.depends('vat', 'parent_id.commercial_partner_id', 'is_company')
    def _compute_commercial_vat(self):
        """Detect vat duplicate just for global partners (companies) avoiding
        children (contacts)"""
        for partner in self.filtered(lambda p: (p.is_company or
                                                not p.parent_id) and p.vat):
            # Replace all special chars and use uppercase in order to raise
            # the exception if a small variation is used.
            partner.commercial_vat = re.sub(r'\W+|\_', '', partner.vat.upper())

    _sql_constraints = [
        ('unique_commercial_vat',
         'unique (commercial_vat,company_id)',
         "Partner's VAT must be a unique value or empty")]
