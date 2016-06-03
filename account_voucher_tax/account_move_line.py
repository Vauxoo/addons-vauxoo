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

from openerp import models, api, exceptions, _


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.multi
    def validate_rounding_high(self):
        for move in self:
            if move.name == _('Rounding error from currency conversion'):
                move_line_amount_rounding = abs(move.debit + move.credit)
                move_line_bank = move.move_id.line_id.filtered(
                    lambda dat: dat.account_id.type == 'liquidity')
                move_line_bank_debit_credit = abs(
                    move_line_bank.debit + move_line_bank.credit)
                if move_line_amount_rounding > move_line_bank_debit_credit:
                    raise exceptions.Warning(
                        _('Warning!'),
                        _('Rounding amount is too high  %s '
                          'and payment bank %s') % (
                              move_line_amount_rounding,
                              move_line_bank_debit_credit))
