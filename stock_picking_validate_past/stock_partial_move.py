# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.osv import osv, fields


class stock_partial_move(osv.TransientModel):
    _inherit = "stock.partial.move"

    def do_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_move, self).do_partial(
            cr, uid, ids, context=context)
        stock_move_obj = self.pool.get('stock.move')
        ids_validate = context.get('active_ids')
        for id_move in ids_validate:
            move = stock_move_obj.browse(cr, uid, id_move)
            type_pross_date = move.type_process_date
            date_expect = move.date_expected
            if type_pross_date == 'planned_date':
                stock_move_obj.write(cr, uid, id_move, {'date': date_expect})

        return res
