# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
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
from openerp.tools.translate import _
import time


class StockInvoiceOnshipping(osv.TransientModel):

    _inherit = 'stock.invoice.onshipping'

    def open_invoice(self, cur, uid, ids, context=None):
        """Overwrite the wizard to first check that the stock picking elements
        have not contract due date, if one of then is expired then will
        raise an exception. If not one is expire will peform the create invoice
        action propertly.
        """
        context = context or {}
        active_ids = context.get('active_ids', False)
        active_model = context.get('active_model', False)
        res = {}
        cr_date = time.strftime('%Y-%m-%d')
        if not active_ids:
            return res
        expire_dates = [
            bool(picking_brw.date_contract_expiry < cr_date)
            for picking_brw in self.pool.get(active_model).browse(cur, uid,
                                                                  active_ids, context=context)
            if picking_brw.date_contract_expiry]
        done_picking = [
            bool(picking_brw.state == 'done')
            for picking_brw in self.pool.get(active_model).browse(cur, uid,
                                                                  active_ids, context=context)]
        if context.get('force_expiry_pickings', False):
            pass
        elif any(expire_dates) or any(done_picking):
            raise osv.except_osv(_('Invalid Procedure'),
                                 _('This action can only be peform over not contract due'
                                   ' date pickings which also are not in done state.'))
        res = super(StockInvoiceOnshipping, self).open_invoice(
            cur, uid, ids, context=context)
        return res
