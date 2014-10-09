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
from openerp.tools.translate import _



class default_price_to_report(osv.TransientModel):

    _name = 'default.price.to.report'

    _columns = {
        'list_price': fields.many2one('product.pricelist', 'List Price'),
        'sure': fields.boolean('Sure?', help="Are sure this operation"),
    }

    def default_price(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        method_obj = self.pool.get('method.price')
        product_obj = self.pool.get('product.product')
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        if wzr_brw.sure:
            if context.get('active_ids'):
                name = wzr_brw.list_price and wzr_brw.list_price.name or False
                name = name.split(' ')
                name = name and name[0] == 'Precio' and name[
                    1].isdigit() and name[1]
                print name
                if name:
                    cost_id = [i.property_cost_structure and
                        i.property_cost_structure.id\
                        for i in product_obj.browse(
                        cr, uid, context.get('active_ids'), context=context)]
                    methods_ids = method_obj.search(cr, uid,
                    [('cost_structure_id', 'in', cost_id), (
                        'default_cost', '=', True)], context=context)
                    if methods_ids:
                        raise osv.except_osv(_('Error'), _(
                            'The product already has a default_cost'))
                    methods_ids = method_obj.search(cr, uid,
                        [('cost_structure_id', 'in', cost_id), (
                        'sequence', '=', int(name))], context=context)
                    method_obj.write(cr, uid, methods_ids, {
                                     'default_cost': True}, context=context)
        else:
            raise osv.except_osv(_('Error'), _('Please select sure option'))
        return {'type': 'ir.actions.act_window_close'}
