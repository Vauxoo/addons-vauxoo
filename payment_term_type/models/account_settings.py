# -*- coding: utf-8 -*-
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
# ###########################################################################
#    Coded by: Hugo Adan (hugo@vauxoo.com)
# ###########################################################################
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
# #############################################################################
from openerp import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    payment_type = fields.Selection([
        ('bqp', 'Based on quantity of payments'),
        ('bdp', 'Based on date of payments')],
        string="Payments terms",
        help='*bqp.- Based on quantity of payments\n'
             'Payments terms will be considered type: \n'
             ' \'Cash Payment\'- '
             'when the payments have been covered in just one exhibition.'
             ' without matter the date of payment \n'
             ' \'Credit Payment\'- '
             'when the payments will be covered in just two or '
             'more exhibitions (partialities). \n'
             '*bdp.- Based on date of payments\n'
             'Payments terms will be considered type: \n'
             ' \'Cash Payment\'- '
             'when the payments have been covered in just one exhibition,'
             ' in the same day that the  sale order be confirmed.\n'
             ' \'Credit Payment\'- '
             'when the payments will be covered in just one or more '
             'exhibitions, but the payments will be done in a different '
             'day that the sale order confirmation day.')

    @api.model
    def get_default_payment_term_type(self, fields_name):
        key_payment = "account.payment_term_type"
        payment_type = self.env["ir.config_parameter"].get_param(
            key_payment, default='bqp')
        return {'payment_type': payment_type}

    @api.one
    def set_default_payment_term_type(self):
        config_parameters = self.env["ir.config_parameter"]
        key_by_company_id = "account.payment_term_type"
        config_parameters.set_param(
            key_by_company_id, self.payment_type or '',)
