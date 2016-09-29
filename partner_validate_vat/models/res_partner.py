# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
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
