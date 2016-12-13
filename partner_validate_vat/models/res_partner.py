# -*- coding: utf-8 -*-
# Copyright (c) 2016 Vauxoo - http://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def _check_vat_uniqueness(self):
        """Check that the vat is unique by company"""
        for partner in self:
            company = self.env['res.users'].browse(partner._uid).company_id
            vat = partner.commercial_partner_id.vat
            if all([company.country_id == partner.country_id, vat,
                    partner.search([
                        ('vat', '=', vat),
                        ('id', 'not in', [
                            partner.commercial_partner_id.id, partner.id]),
                        ('commercial_partner_id', '!=',
                         partner.commercial_partner_id.id)
                    ])]):
                raise ValidationError(
                    _("Error ! Partner's VAT must be unique."))

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'vat': False,
        })
        return super(ResPartner, self).copy(default)
