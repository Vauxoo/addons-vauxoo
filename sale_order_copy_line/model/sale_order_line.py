# coding: utf-8
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#

#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

from openerp.osv import osv
from openerp.tools.translate import _


class SaleOrderLine(osv.Model):

    _inherit = 'sale.order.line'

    def sale_order_line_copy(self, cr, uid, ids, context=None):
        data = self.copy_data(cr, uid, ids[0], context=context)
        sale_order_obj = self.pool.get('sale.order')
        data_sale_order = sale_order_obj.browse(cr, uid, data.get('order_id'))

        if data_sale_order.state in ('draft', 'sent'):
            self.create(cr, uid, data, context=context)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'sale.order',
                'res_id': data.get('order_id'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'nodestroy': True, }
        else:
            raise osv.except_osv(_('Error!'), _(
                "This sale order is not in draft state"))
