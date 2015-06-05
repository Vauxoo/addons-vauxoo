#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp.osv import fields, osv


class product_price_list(osv.osv_memory):
    _inherit = 'product.price_list'
    _description = 'Price List'
    _rec_name = 'price_list'

    _columns = {
        'report_format': fields.selection([
            ('pdf', 'PDF'),
            # TODO: enable print on controller to HTML
            # ('html', 'HTML'),
            ('xls', 'Spreadsheet')], 'Report Format'),
        'cost': fields.boolean('Cost'),
        'margin_cost': fields.boolean('Exp. Marg. Cost (%)'),
        'margin_sale': fields.boolean('Exp. Marg. Sale (%)'),
    }
    _defaults = {
        'report_format': lambda *args: 'xls',
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        datas = {'ids': context.get('active_ids', [])}

        field_list = ['price_list', 'qty1',
                      'qty2', 'qty3', 'qty4', 'qty5', 'report_format',
                      'margin_cost', 'margin_sale']

        res = self.read(cr, uid, ids, field_list, load=None,
                        context=context)
        res = res and res[0] or {}

        if res.get('margin_cost') or res.get('margin_sale'):
            res['qty1'] = 1.0
            for idx in range(2, 6):
                res['qty%d' % idx] = 0.0

        context['xls_report'] = res.get('report_format') == 'xls'

        datas['form'] = res

        return self.pool['report'].get_action(
            cr, uid, [], 'product.report_pricelist', data=datas,
            context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
