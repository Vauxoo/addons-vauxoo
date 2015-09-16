# coding: utf-8
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
from openerp.tools.translate import _


class ChangeNumber(osv.TransientModel):

    _name = 'change.number'
    _columns = {
        'number': fields.char('New Number', 20,
                              help="Enter the new number of the invoice"),
        'sure': fields.boolean('Are sure?',
                               help="Select to number change"),

    }

    def change_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('account.move')
        if context.get('active_id'):
            wzr_brw = self.browse(cr, uid, ids, context=context)[0]
            if wzr_brw.sure:
                invo_brw = invo_obj.browse(cr, uid, context.get(
                    'active_id'), context=context)
                invo_brw.move_id and move_obj.write(cr, uid, [
                    invo_brw.move_id.id],
                    {'name': wzr_brw.number}, context=context)
                invo_obj.write(cr, uid, [invo_brw.id], {
                               'internal_number': wzr_brw.number},
                               context=context)
            else:
                raise osv.except_osv(_('Invalid action !'), _(
                    "Must be sure the operation"))
        return {'type': 'ir.actions.act_window_close'}
