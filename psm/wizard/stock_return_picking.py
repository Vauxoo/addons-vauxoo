# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import openerp.netsvc as netsvc
import time

from openerp.osv import osv, fields
from openerp.tools.translate import _



class stock_return_picking(osv.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(stock_return_picking, self).create_returns(
            cr, uid, ids, context=context)

        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        spl_obj = self.pool.get('stock.production.lot')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        for move in pick.move_lines:
            spl_obj.write(cr, uid, [
                          move.prodlot_id.id], {'check_serial': False})

        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
