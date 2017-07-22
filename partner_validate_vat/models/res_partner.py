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
        """Check that the vat is unique in the level where the partner is
        in the tree
        """

        user_company = self.env.user.company_id

        for partner in self.filtered(
                lambda r: r.country_id == user_company.country_id and
                r.vat is not False):
            current_commercial = partner.commercial_partner_id
            if not current_commercial:
                current_commercial = partner.browse(
                    partner._commercial_partner_compute(
                        self.env.cr, 'commercial_parent_id')[partner.id])
            if (partner.search([
                    ('vat', '=', current_commercial.vat),
                    ('commercial_partner_id', '!=',
                     current_commercial.id)], limit=1)):
                raise ValidationError(_("Partner's VAT must be a unique "
                                        "value or empty"))
