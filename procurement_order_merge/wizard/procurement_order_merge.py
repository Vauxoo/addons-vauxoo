# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
from openerp.osv import osv
from openerp.tools.translate import _


class procurement_order_merge(osv.TransientModel):
    _name = 'procurement.order.merge'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(procurement_order_merge, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=False)
        if context.get('active_model', '') == 'procurement.order' and\
                len(context['active_ids']) < 2:
            raise osv.except_osv(_('Warning'),
                                 _('Please select multiple order to merge\
                                    in the list view.'))
        return res

    def procurement_merge(self, cr, uid, ids, context=None):
        procurement_order = self.pool.get('procurement.order')
        if context is None:
            context = {}
        procurement_ids = context.get('active_ids', [])
        procurement_order.do_merge(cr, uid, procurement_ids, context=context)
        return {}
