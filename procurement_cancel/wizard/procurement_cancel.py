# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import logging

from openerp.osv import osv

_logger = logging.getLogger(__name__)


class cancel_procurement_order(osv.osv_memory):
    _name = 'cancel.procurement.order'
    _description = 'Cancel procurement'

    def cancel_procurement(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """

        pr_obj = self.pool['procurement.order']
        _logger.info('Cancel Procurement is running')
        for procurement_id in context.get('active_ids', False):
            state = pr_obj.browse(cr, uid, procurement_id,
                                  context=context).state
            if state in ('exception', 'confirmed', 'running'):
                pr_obj.write(cr, uid, procurement_id, {'state': 'cancel'},
                             context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
