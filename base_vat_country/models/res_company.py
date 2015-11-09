# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from openerp import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat_without_country = fields.Char(
        'TIN', help='Tax Identification Number. You no set the prefix of '
        'country.', related='partner_id.vat_without_country')
    country_code = fields.Char(
        'Country Code', help='Added the country code in partner',
        readonly=True, related='country_id.code', size=2)

    @api.onchange('vat_without_country', 'country_id')
    def onchange_date(self):
        if self.vat_without_country:
            self.vat = (self.country_id and self.country_id.code or '  ') +\
                self.vat_without_country
        else:
            self.vat = ''
