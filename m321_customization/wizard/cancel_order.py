# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _

import datetime


class cancel_orders(osv.TransientModel):

    """
    M321 Customizations to cancel orders that are confirmed but are not paid
    """
    _name = "cancel.orders"

    _columns = {
        'sure': fields.boolean("Sure?", help="Check if are sure"),
        'are_sure': fields.boolean("Are Sure?",
            help="Check if really are sure"),
        'n_days': fields.integer('Number Days',
            help="Number of day to cancel sales orders by defaults 2")
    }
    _defaults = {
        'n_days': 2

    }

    def cancel_orders(self, cr, uid, ids=False, days=1, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        journal_ids = journal_obj.search(cr, uid, [], context=context)
        [journal_obj.write(cr, uid, [i.id],
            {'update_posted': True}, context=context)
            for i in journal_obj.browse(cr, uid, journal_ids, context=context)
            if hasattr(i, "update_posted")
            if i.type in ('sale', 'sale_refund')]
        wz_brw = ids and self.browse(cr, uid, ids[0], context=context) or False
        evalu = wz_brw and 'wz_brw.sure and wz_brw.are_sure' or 'True'
        date = datetime.datetime.today()
        date = date and date - datetime.timedelta(
            days=wz_brw and eval('wz_brw.n_days') or days)
        date = date and date.strftime('%Y-%m-%d')
        sales_ids = sale_obj.search(cr, uid, [(
            'date_order', '<=', date)], context=context)
        sale_brw = sales_ids and sale_obj.browse(
            cr, uid, sales_ids, context=context)
        sale_ids = []
        if eval(evalu) and sale_brw:
            for sale in sale_brw:
                if sale.state in ('manual', 'progress'):
                    pick = [False for pick in sale.picking_ids
                            if pick and pick.state in ('confirmed', 'done')]
                    invoice = [False for invoice in sale.invoice_ids
                               if invoice and invoice.state in
                               ('paid', 'open')]
                    all(pick) and all(invoice) and sale_ids.append(sale.id)

            sale_ids and picking_obj.action_cancel(cr, uid,
                [d.id for i in sale_obj.browse(
                    cr, uid, sale_ids, context=context) for d in i.picking_ids],
                context=context)
            sale_ids and invoice_obj.action_cancel(cr, uid,
                [d.id for i in sale_obj.browse(
                    cr, uid, sale_ids, context=context) for d in i.invoice_ids],)
            sale_ids and sale_obj.action_cancel(
                cr, uid, sale_ids, context=context)

        else:
            raise osv.except_osv(_('Processing Error'), _(
                'Must select the 2 options to make sure the operation'))
        return {'type': 'ir.actions.act_window_close'}
