# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
# ###########################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication:
#             * Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp import models, api
import time


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    # pylint: disable=W0622
    # @api.one
    # def compute(self, value, date_ref=False):
    #     if date_ref:
    #         try:
    #             date_ref = time.strftime(
    #                 '%Y-%m-%d', time.strptime(date_ref, '%Y-%m-%d %H:%M:%S'))
    #         except BaseException:
    #             pass
    #     result = super(AccountPaymentTerm, self).compute(value, date_ref)
    #     return result[0][0][0]
