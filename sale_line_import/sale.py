# coding: utf-8
###########################################################################
#    Module Writen to odoo, Open Source Management Solution
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

import csv
import io
import odoo.tools as tools
from odoo import models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def import_data_line(self, cr, uid, ids, fdata, favalidate, context={}):
        order = self.pool.get('sale.order').browse(cr, uid, ids)
        input = io.StringIO(fdata)
        input.seek(0)
        data = list(csv.reader(input, quotechar='"' or '"', delimiter=','))
        data[0].append('order_id.id')
        try:
            list_prod = data[0].index('product_id')
        except:
            list_prod = []
        msg = ''
        pmsg = ''
        not_products = []
        new_products_prices = []
        for dat in data[1:]:
            datas = []
            data2 = list(data[0])
            dat.append(ids)
            try:
                prod_name = dat[list_prod]
            except:
                prod_name = False
            context.update({'partner_id': order.partner_id.id})
            prod_name_search = prod_name and self.pool.get(
                'product.product').name_search(cr, uid, prod_name,
                                               context=context) or False
            prod_id = prod_name_search and prod_name_search[0][0] or False
            lines = prod_id and self.pool.get(
                'sale.order.line').product_id_change(cr, uid, [],
                                                     order.pricelist_id.id,
                                                     prod_id, qty=0, uom=False,
                                                     qty_uos=0, uos=False,
                                                     name='',
                                                     partner_id=order.partner_id.id,
                                                     lang=False,
                                                     update_tax=True,
                                                     date_order=False,
                                                     packaging=False,
                                                     fiscal_position=False,
                                                     flag=False,).get('value',
                                                                      False)\
                or {}
            if not lines and prod_name:
                not_products.append(prod_name)
            if not prod_name:
                self.pool.get('sale.order.line').import_data(
                    cr, uid, data2, [dat], 'init', '')
            for lin in range(len(lines.keys())):
                if lines.keys()[lin] not in data[0]:
                    if lines.keys()[lin] in ('tax_id', 'product_uom',
                                             'product_packaging'):
                        field_val = str(lines.keys()[lin])
                        field_val = field_val + '.id'
                        data2.append(field_val)
                        vals_many = str(lines[lines.keys()[lin]]).replace(
                            '[', '').replace(']', '').replace('False', '')
                        dat.append(vals_many)
                    else:
                        data2.append(lines.keys()[lin])
                        dat.append(lines[lines.keys()[lin]])
                else:
                    val_str = dat[data[0].index(lines.keys()[lin])]
                    val_str_2 = lines[lines.keys()[lin]]
                    if lines.keys()[lin] == 'product_uom':
                        val_str_2 = self.pool.get(
                            'product.uom').browse(cr, uid, val_str_2).name
                        val_str = dat[data[0].index(lines.keys()[lin])]
                    if lines.keys()[lin] == 'price_unit':
                        product_price = []
                        product_price.append(prod_name)
                        val_str = float(dat[data[0].index(lines.keys()[lin])])
                        val_str_2 = float(lines[lines.keys()[lin]])
                        if tools.ustr(val_str) != tools.ustr(val_str_2):
                            product_price.append(val_str)
                            product_price.append(val_str_2)
                            new_products_prices.append(product_price)
                    try:
                        val_str = float(val_str)
                        val_str_2 = float(val_str_2)
                    except:
                        pass
                    if val_str != val_str_2:
                        if not lines.keys()[lin] == 'price_unit':
                            pmsg += _('%s , Field: %s, CSV: %s, OPEN: %s \n')\
                                % (tools.ustr(prod_name),
                                   lines.keys()[lin],
                                   tools.ustr(dat[data[0].
                                                  index(lines.keys()[lin])]),
                                   tools.ustr(val_str_2))
                        if favalidate:
                            dat[data[0].index(lines.keys()[lin])] = val_str_2
                        else:
                            dat[data[0].index(lines.keys()[
                                              lin])] = val_str or val_str_2
            datas.append(dat)
            try:
                lines and self.pool.get('sale.order.line').import_data(
                    cr, uid, data2, datas, 'init', '', context=context) or\
                    False
            except Exception, e:
                return False
            data2 = []

        msg += _('Do not you find reference:')
        msg += '\n'
        for p in not_products:
            msg += '%s \n' % (tools.ustr(p))
        msg += '\n'
        msg += _(
            '''Warning of price difference, CSV VS System in
               the following products:''')
        msg += '\n'
        for p in new_products_prices:
            p2 = (','.join(map(str, p)))
            msg += '%s \n' % (p2)
        msg += '\n'
        msg += _(
            '''Warning differences in other fields,
               CSV VS System in the following products and fields:''')
        msg += '\n %s ' % (pmsg)
        msg2 = tools.ustr(pmsg)
        msg = tools.ustr(msg) + '%s ' % (msg2)
        return msg
