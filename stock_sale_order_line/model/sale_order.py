# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
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

from openerp.osv import osv, fields


class stock_move(osv.osv):

    _inherit = 'stock.move'
    _columns = {
        'sale_line_id': fields.related(
            'procurement_id',
            'sale_line_id',
            string='Sale Order Line',
            type='many2one',
            relation='sale.order.line',
            readonly=True,
            store=True,
            ondelete='set null'),
    }


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'
    _columns = {
        'move_ids': fields.one2many(
            'stock.move', 'sale_line_id',
            'Reservation',
            readonly=True,
            ondelete='set null'),
    }
