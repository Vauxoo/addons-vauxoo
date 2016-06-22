# coding: utf-8
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


class ProductPriceList(osv.osv_memory):
    _inherit = 'product.price_list'
    _description = 'Price List'
    _rec_name = 'price_list'

    _columns = {
        'report_format': fields.selection([
            ('pdf', 'PDF'),
            # TODO: enable print on controller to HTML
            # ('html', 'HTML'),
            ('xls', 'Spreadsheet')], 'Report Format', default='xls'),
        'cost': fields.boolean('Cost'),
        'margin_cost': fields.boolean('Exp. Marg. Cost (%)'),
        'margin_sale': fields.boolean('Exp. Marg. Sale (%)'),
        'only_prod_pricelist': fields.boolean(
            'Only products in pricelist', help='If you active this field the '
            'products that are not in pricelist will have in the report the '
            'price in zero', default=True),
        'products_with_price': fields.boolean(
            'Only products with price', help='If this field is active, only '
            'will to add the products that have price.'
        )
    }

    def print_report(self, cr, uid, ids, context=None):
        """To get the date and print the report
        @return : return report
        """
        context = context and dict(context) or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        datas = {'ids': context.get('active_ids', [])}

        field_list = [
            'price_list', 'qty1', 'qty2', 'qty3', 'qty4', 'qty5',
            'report_format', 'margin_cost', 'margin_sale',
            'only_prod_pricelist', 'products_with_price']

        res = self.read(cr, uid, ids, field_list, load=None,
                        context=context)
        res = res and res[0] or {}

        if res.get('margin_cost') or res.get('margin_sale'):
            res['qty1'] = 1.0
            for idx in range(2, 6):
                res['qty%d' % idx] = 0.0

        context['xls_report'] = res.get('report_format') == 'xls'
        context.update({
            'only_prod_pricelist': res.get('only_prod_pricelist', False),
            'products_with_price': res.get('products_with_price', False)})

        datas['form'] = res

        return self.pool['report'].get_action(
            cr, uid, [], 'product.report_pricelist', data=datas,
            context=context)
