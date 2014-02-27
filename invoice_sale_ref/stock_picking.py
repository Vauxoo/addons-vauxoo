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


from openerp.osv import fields, osv


class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cursor, user, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        picking_id__invoice_id_dict = super(
            stock_picking, self).action_invoice_create(cursor, user, ids,
                                                        journal_id=journal_id,
                                                        group=group, type=type,
                                                        context=context)
        invoice_id__client_order_ref_dict = {}
        for picking_id in picking_id__invoice_id_dict.keys():
            invoice_id = picking_id__invoice_id_dict[picking_id]
            picking = picking_obj.browse(
                cursor, user, picking_id, context=context)
            invoice_id__client_order_ref_dict.setdefault(invoice_id, []).append(
                picking.sale_id and picking.sale_id.client_order_ref or '')
        for invoice_id in invoice_id__client_order_ref_dict:
            client_order_ref_list = invoice_id__client_order_ref_dict[
                invoice_id]
            client_order_ref_str = ','.join(map(
                lambda x: str(x), client_order_ref_list))
            invoice_obj.write(cursor, user, [invoice_id], {
                              'name': client_order_ref_str}, context=context)
        return picking_id__invoice_id_dict
