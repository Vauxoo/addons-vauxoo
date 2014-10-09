# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
from openerp.osv import osv
from openerp.tools.translate import _


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def search_asociated_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_pool = self.pool.get('ir.model.data')
        inv_type = self.read(cr, uid, ids[0], ['type', 'name'])
        name = inv_type['name']
        inv_type = inv_type['type']
        invoice_ids = self.search(cr, uid, [('name', '=', name)])
        # inv_type = context.get('inv_type', False)
        action_model = False
        action = {}
        if not invoice_ids:
            raise osv.except_osv(_('Error'), _('No Invoices were created'))
        if inv_type == "out_invoice":
            action_model, action_id = data_pool.get_object_reference(
                cr, uid, 'account', "action_invoice_tree1")
        elif inv_type == "in_invoice":
            action_model, action_id = data_pool.get_object_reference(
                cr, uid, 'account', "action_invoice_tree2")
        elif inv_type == "out_refund":
            action_model, action_id = data_pool.get_object_reference(
                cr, uid, 'account', "action_invoice_tree3")
        elif inv_type == "in_refund":
            action_model, action_id = data_pool.get_object_reference(
                cr, uid, 'account', "action_invoice_tree4")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', [" + ','.join(
                map(str, invoice_ids)) + "])]"
            action.update({'nodestroy': True})
        return action
