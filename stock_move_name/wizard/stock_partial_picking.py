# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
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


from openerp.osv import fields, osv


class stock_partial_picking_line(osv.TransientModel):

    _inherit = "stock.partial.picking.line"
    _columns = {
        'name': fields.char('Description'),
    }


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move, context=None):
        context = context or {}
        partial_move = super(stock_partial_picking,
                             self)._partial_move_for(cr, uid, move)
        partial_move['name'] = move.name
        return partial_move

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
