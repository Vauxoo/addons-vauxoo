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

        for partner in self.mapped('commercial_partner_id').filtered('vat'):
            if (user_company.country_id == partner.country_id and
                partner.search([
                    ('vat', '=', partner.vat),
                    ('commercial_partner_id', '!=',
                     partner.id)], limit=1)):
                raise ValidationError(_("Partner's VAT must be a unique "
                                        "value or empty"))
