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
##########################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp import workflow

wf_service = workflow


class ValidatePicking(osv.TransientModel):

    _name = 'validate.picking.wz'

    _columns = {
        'sure': fields.boolean('Sure', help="Are sure this operation"),
        'confirm': fields.boolean('Confirm', help="Are sure this operation"),
    }

    def validate_picking(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        stock_obj = self.pool.get(context.get('active_model', 'stock.move'))
        model = context.get('active_model', 'stock.move')
        model = model.split('.')
        model = model and model[1]
        do_partial = self.pool.get('stock.partial.%s' % model)
        copy_ctx = context.copy()

        for wzr_brw in self.browse(cr, uid, ids, context=context):
            if wzr_brw.sure and wzr_brw.confirm:
                if context.get('active_ids'):
                    if 'stock.picking' in context.get('active_model'):
                        stock_obj.draft_validate(cr, uid,
                                                 context.get('active_ids'))
                        for pick in stock_obj.browse(cr, uid,
                                                     context.get('active_ids'),
                                                     context=context):
                            copy_ctx.update({'active_ids': [pick.id]})
                            dicts = do_partial.default_get(cr, uid,
                                                           ['picking_id',
                                                            'move_ids',
                                                            'date'], copy_ctx)
                            dicts.get('move_ids') and \
                                dicts.update({'move_ids': [(0, 0, i)
                                                           for i in dicts.get(
                                                               'move_ids')]})
                            partial_id = do_partial.create(cr, uid, dicts)
                            do_partial.do_partial(cr, uid,
                                                  [partial_id], copy_ctx)
                    elif 'stock.move' in context.get('active_model'):
                        context.update({'no_change_date': True})
                        stock_obj.action_done(cr, uid,
                                              context.get('active_ids'),
                                              context=context)
            else:
                raise osv.except_osv(_('Error'),
                                     _('Please select the checkbox'))
        return {'type': 'ir.actions.act_window_close'}
