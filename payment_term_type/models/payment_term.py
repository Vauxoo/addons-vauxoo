# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Vauxoo Consultores (info@vauxoo.com)
############################################################################
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
##############################################################################

from openerp import models, api, fields, _


class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'

    @api.multi
    @api.depends('line_ids')
    def _compute_payment_type(self):
        """This method compute the Payment type
            It is cash when payment term
            has only one line to compute,
            It is credit when payment term has
            at least two line to compute
        """
        key_payment = "account.payment_term_type"
        payment_type = self.env["ir.config_parameter"].get_param(
            key_payment, default='bqp')
        for record in self:
            if payment_type == 'bqp':
                record.payment_type = 'cash'
                if len(record.line_ids) > 1:
                    record.payment_type = 'credit'
            elif payment_type == 'bdp':
                for line in record.line_ids:
                    record.payment_type = 'cash'
                    if line.days > 0:
                        record.payment_type = 'credit'

    payment_type = fields.Selection(
        [('credit', _('Credit')),
         ('cash', _('Cash'))],
        string="Payment Type", compute='_compute_payment_type',
        help="Consult the Payment Terms in accounting settings: ( Based on "
        "quantity of payments or Based on date of payments ) \n "
        "-Credit: The payment term will be credit type when the payments "
        "are covered in just two ore more exhibitions (partialities) or \n"
        "when the payments are covered in just one or more "
        "exhibitions, but the payments will be done in a different "
        "day that the sale order confirmation day.\n"
        "-Cash: The payment term will be cash type when the payments "
        "have been covered in just one exhibition. without matter the date of "
        "payment or when the payments have been covered in just "
        "one exhibition, in the same day that the  sale order be confirmed."
    )
