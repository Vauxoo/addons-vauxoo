# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>,
#              Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Yanina Aular <yani@vauxoo.com>
#    Audited by: Moises Lopez <moylop260@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import fields, models, api
from openerp.tools.translate import _


class res_partner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _get_location_options(self):
        """
        @return a list of tuples with the selection field options.
        """
        return [('undefine', 'Undefine'),
                ('international', 'International'),
                ('national', 'National')]

    @api.depends('country_id')
    def _get_partner_scope(self):
        """
        @return dictionary {res.partner.id: selecction field value}
        """

        for rp_brw in self:
            rp_brw.international = 'undefine'

        company_country = self.env['res.users'].browse(self._uid).\
            company_id.country_id.id or False
        if company_country:
            for rp_brw in self:
                rp_brw.international = rp_brw.country_id.id != company_country and \
                    'international' or 'national'

    @api.depends('international')
    def _get_warning_message(self):
        """
        @return dictionary {res.partner id: message value}
        """
        msg = _('Missing Configuration: international/national partner'
                ' data is set using your configurate company country.\n'
                'Please configurate your company country in order to'
                ' view your suppliers/customer information correctly')
        for rp_brw in self:
            if rp_brw.international == 'undefine':
                rp_brw.message = msg

    international = \
        fields.Selection(_get_location_options,
                         compute='_get_partner_scope',
                         string='Location Type',
                         help="Show the location value of the "
                         "partner taking into account"
                         " your company country information."
                         " - National: is a local partner "
                         "(same country as your company)."
                         " - International: the partner is in foreign country."
                         " - Undefined: your company country is not set so the"
                         "   location type cannot be compute.")

    message = fields.Text(compute='_get_warning_message', string='Message')
