# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2017 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: jorge_nr (jorge_nr@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(copy=False)

    @api.multi
    @api.constrains('vat')
    def _check_vat_uniqueness(self):
        """ Check that the vat is unique in the level
            where the partner in the tree
        """

        user_company = self.env.user.company_id

        for partner in self:
            current_vat = partner.vat

            if all([user_company.country_id == partner.country_id, current_vat,
                    partner.search([
                        ('vat', '=', current_vat),
                        ('id', 'not in', [partner.parent_id.id, partner.id]),
                        ('parent_id', '!=', partner.parent_id.id)
                    ], limit=1)]):
                raise ValidationError(_("Partner's VAT must be a unique "
                                        "value or empty"))
