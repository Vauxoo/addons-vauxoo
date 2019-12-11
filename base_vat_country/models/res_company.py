from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    vat_without_country = fields.Char(
        'TIN', readonly=False, related='partner_id.vat_without_country',
        help='Tax Identification Number. You no set the country prefix.')
    country_code = fields.Char(
        help='Added the country code in partner, to complete the NIF.',
        related='country_id.code', size=2)

    @api.onchange('vat_without_country', 'country_code')
    def onchange_vat_wo_country(self):
        if self.vat_without_country:
            self.vat = (self.country_code or '  ') + self.vat_without_country
        else:
            self.vat = ''
