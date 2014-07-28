#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
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

from openerp.osv import osv

class stock_move(osv.osv):
    _inherit = "stock.move"
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        res = super(stock_move, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=context)
        if move.purchase_line_id and move.purchase_line_id.analytics_id:
            debit_line_vals, credit_line_vals = res[0][2],res[1][2]
            debit_line_vals['analytics_id'] = move.purchase_line_id.analytics_id.id
            credit_line_vals['analytics_id'] = move.purchase_line_id.analytics_id.id
            res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res

