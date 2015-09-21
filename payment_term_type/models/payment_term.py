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

    @api.one
    @api.depends('line_ids')
    def _compute_payment_type(self):
        """
            This method compute the Payment type
            It is cash when payment term
            has only one line to compute,
            It is credit when payment term has
            at least two line to compute
        """

        self.payment_type = 'cash'
        if len(self.line_ids) > 1:
            self.payment_type = 'credit'

    payment_type = fields.Selection(
        [('credit', _('Credit')),
         ('cash', _('Cash'))],
        string="Payment Type", compute='_compute_payment_type', store=True)
