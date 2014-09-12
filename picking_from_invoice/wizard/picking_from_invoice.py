#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields
import openerp.tools as tools
from openerp.tools.translate import _

from tools import config
import openerp.netsvc as netsvc
from openerp.addons.decimal_precision import decimal_precision as dp
import time


class picking_from_invoice(osv.TransientModel):

    _name = 'picking.from.invoice'
    _columns = {
        'invoice_ids': fields.many2many('account.invoice', 'invoice_rel',
            'invoice1', 'invoice2', 'Invoices',
            help="Select the invoices to account move cancel"),

    }

    def generate_picking(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        warehouse_obj = self.pool.get('stock.warehouse')
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, 'picking.from.invoice', context=context)
        ware_ids = warehouse_obj.search(cr, uid, [(
            'company_id', '=', company_id)], context=context)
        if not ware_ids:
            raise osv.except_osv(_('Invalid action !'), _(
                'You cannot  create picking because you not\
                have a warehouse!'))
        ware_brw = ware_ids and warehouse_obj.browse(
            cr, uid, ware_ids[0], context=context) or False
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        for invoice in wzr_brw.invoice_ids:
            for line in invoice.invoice_line:
                if invoice.type in ('in_invoice', 'out_invoice'):
                    pick_name = self.pool.get('ir.sequence').get(cr,
                                uid, 'stock.picking.%s' % (invoice and
                                      invoice.type == 'in_invoice' and
                                      'in' or invoice.type == 'out_invoice' and
                                      'out'))
                    picking_id = self.pool.get('stock.picking').create(cr, uid, {
                        'name': pick_name,
                        'origin': invoice.name,
                        'type': invoice and
                        invoice.type == 'in_invoice' and
                                        'in' or invoice.type == 'out_invoice'\
                                        and 'out',
                        'state': 'auto',
                        'move_type': 'direct',
                        'address_id': invoice.partner_id and
                                        invoice.partner_id.address and
                                        invoice.partner_id.address[0].id,
                        'note': invoice.comment,
                        'invoice_state': 'invoiced',
                        'company_id': invoice.company_id.id,
                    })
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': line.name[:64],
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date': invoice.date_invoice,
                        'date_expected': invoice.date_invoice,
                        'product_uom': line.uos_id.id,
                        'product_qty': line.quantity,
                        'product_uos': line.uos_id and line.uos_id.id,
                        'address_id': invoice.partner_id and
                                        invoice.partner_id.address and
                                        invoice.partner_id.address[0].id,
                        'location_id': ware_brw and ware_brw.lot_stock_id and
                                        ware_brw.lot_stock_id.id,
                        'location_dest_id': ware_brw and
                                            ware_brw.lot_output_id and
                                            ware_brw.lot_output_id.id,
                        'tracking_id': False,
                        'state': 'draft',
                        'note': line.note,
                        'company_id': invoice.company_id.id,
                    })

        return {'type': 'ir.actions.act_window_close'}
