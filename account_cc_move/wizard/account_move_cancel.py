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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import netsvc
import decimal_precision as dp
from DateTime import DateTime
import time

invo_cost = {}


class account_move_cancel(osv.osv_memory):

    _name = 'account.move.cancel'
    _columns = {
        'invoice_ids': fields.many2many('account.invoice', 'invoice_rel', 'invoice1', 'invoice2', 'Invoices', help="Select the invoices to account move cancel"),

    }

    def cancel_account_move(self, cr, uid, ids, context=None, invoice_ids=False):
        '''
            Cancel invoices to delete account move
            @param invoice_ids, ids list of invoices to method apply
            @param ids, ids of wizard if called from this
        '''

        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        move_ids = invoice_ids and [i.move_id.id for i in invo_obj.browse(cr, uid, invoice_ids, context=context) if i.move_id] or [
            i.move_id.id for i in self.browse(cr, uid, ids, context=context)[0].invoice_ids if i.move_id]
        invo_ids = invoice_ids or [i.id for i in self.browse(
            cr, uid, ids, context=context)[0].invoice_ids if i.move_id]

        journal_ids = journal_obj.search(cr, uid, [], context=context)
        hasattr(journal_obj.browse(cr, uid, journal_ids[0], context=context), 'update_posted') and \
            journal_obj.write(cr, uid, journal_ids, {
                              'update_posted': True}, context=context)
        account_move_obj = self.pool.get('account.move')
        if move_ids:
            invo_obj.write(cr, uid, invo_ids, {
                           'move_id': False}, context=context)
            account_move_obj.button_cancel(cr, uid, move_ids, context=context)
            account_move_obj.unlink(cr, uid, move_ids, context=context)
            invo_obj.action_move_create(cr, uid, invo_ids, ())

        return True


account_move_cancel()



    # nombre del modulo account_anglo_saxon_cost_structure

#~ acttion_cancel asiento (acount_move)
#~ action_move_create (account_invoice)
