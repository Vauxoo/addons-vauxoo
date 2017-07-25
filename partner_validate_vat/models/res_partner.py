# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(copy=False)

    @api.constrains('vat', 'country_id', 'commercial_partner_id')
    def _check_vat_uniqueness(self):
        """Check that the partner's vat is unique among partners of the same
        company
        1.- Validate that the partner's vat is unique, in relation to another
        partner, excluding those related to the commercial_parent_id field.
        2.- Validate that the partners belong to the same company through
        the country_id field, since two partners or more can have same vat
        but is from different countries.
        3.- The partners that are related have the same fields: vat,
        commercial_parent_id, country_id
        """

        user_company = self.env.user.company_id

        # Check if it belongs to the same company in relation to point 2
        for partner in self.filtered(
                lambda r: r.country_id == user_company.country_id and r.vat):
            current_commercial = partner.commercial_partner_id
            if not current_commercial:
                current_commercial = partner.browse(
                    partner._commercial_partner_compute(
                        self.env.cr, 'commercial_parent_id')[partner.id])
            # Search partner with the same vat in relation to points 1 and 3
            if (partner.search([
                    ('vat', '=', current_commercial.vat),
                    ('commercial_partner_id', '!=', current_commercial.id)
                    ], limit=1)):
                raise ValidationError(_("Partner's VAT must be a unique "
                                        "value or empty"))
