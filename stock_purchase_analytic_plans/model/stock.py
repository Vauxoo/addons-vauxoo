# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp import models, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _prepare_account_move_line(self, move, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockQuant, self)._prepare_account_move_line(
            move, qty, cost, credit_account_id, debit_account_id)
        purchase_line_id = move.purchase_line_id
        if not purchase_line_id and move.origin_returned_move_id:
            purchase_line_id = move.origin_returned_move_id.purchase_line_id
        if purchase_line_id and purchase_line_id.analytics_id:
            debit_line_vals, credit_line_vals = res[0][2], res[1][2]
            if move.location_dest_id.usage == 'internal':
                debit_line_vals[
                    'analytics_id'] = purchase_line_id.analytics_id.id
            else:
                credit_line_vals[
                    'analytics_id'] = purchase_line_id.analytics_id.id
            res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
