# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat_without_country = fields.Char(
        'TIN', related='partner_id.vat_without_country',
        help='Tax Identification Number. You no set the country prefix.')
    country_code = fields.Char(
        help='Added the country code in partner, to complete the NIF.',
        readonly=True, related='country_id.code', size=2)

    @api.onchange('vat_without_country', 'country_code')
    def onchange_vat_wo_country(self):
        if self.vat_without_country:
            self.vat = (self.country_code or '  ') + self.vat_without_country
        else:
            self.vat = ''
