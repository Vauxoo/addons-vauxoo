# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

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
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        key_payment = "account.payment_term_type"
        payment_type = self.env["ir.config_parameter"].get_param(
            key_payment, default='bqp')
        res.update(payment_type=payment_type)
        return res

    @api.multi
    def set_values(self):
        super(AccountConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"]
        key_by_company_id = "account.payment_term_type"
        config_parameters.set_param(
            key_by_company_id, self.payment_type or '',)
