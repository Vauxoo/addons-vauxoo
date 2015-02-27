# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import fields, osv
from openerp.addons.account.wizard import account_invoice_refund as air
from openerp.tools import float_compare


class account_invoice_refund(osv.osv_memory):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    filter_refund_inh = \
        air.account_invoice_refund._columns.get('filter_refund').__dict__
    REFUND_METHOD = filter_refund_inh.get('selection')
    REFUND_METHOD.append(('early_payment',
                         'Early payment: Discount early payment'))

    def _search_xml_id(self, cur, uid, model, record_xml_id, context=None):
        if context is None:
            context = {}
        imd_obj = self.pool.get('ir.model.data')
        res_id = False
        imd_id = imd_obj.search(cur, uid,
                                [('module', '=', model),
                                 ('name', '=', record_xml_id)])
        if imd_id:
            res_id = imd_obj.browse(cur, uid, imd_id)[0].res_id
        return res_id

    def _compute_amount(self, cur, uid, ids, field_names,
                        arg=None,
                        context=None,
                        query='', query_params=()):
        if context is None:
            context = {}
        res = {}
        for wzd in self.browse(cur, uid, ids, context=context):
            res[wzd.id] = wzd.percent * 10

        return res

    def default_get(self, cur, uid, fields_data, context=None):
        if context is None:
            context = {}
        ret = super(account_invoice_refund, self).default_get(cur, uid,
                                                              fields_data,
                                                              context=context)
        active_id = context.get('active_id', False)
        if active_id:
            ret['active_id'] = active_id
        return ret

    def onchange_amount_total(self, cur, uid, ids, percent=0.0,
                              active_id=None, context=None):
        if context is None:
            context = {}
        inv_obj = self.pool.get('account.invoice')
        inv = inv_obj.browse(cur, uid, active_id, context=context)
        return {
            'value': {
                'amount_total': inv.amount_total * (percent / 100),
            }
        }

    _columns = {
        'filter_refund': fields.selection(
            REFUND_METHOD,
            "Refund Method",
            required=True,
            help='Refund base on this type. You can not\
                  Modify and Cancel if the invoice is already reconciled'),
        'percent': fields.float('Percent'),
        'product_id': fields.many2one('product.product', string='Product'),
        'amount_total': fields.float('Amount'),
        'active_id': fields.integer('Active ID'),
    }

    def compute_refund(self, cur, uid, ids, mode='refund', context=None):
        if context is None:
            context = {}

        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        account_m_line_obj = self.pool.get('account.move.line')

        result = super(account_invoice_refund,
                       self).compute_refund(cur, uid,
                                            ids, mode,
                                            context=context)
        refund_id = result.get('domain')[1][2]

        wizard_brw = self.browse(cur, uid, ids, context=context)
        percent = wizard_brw.percent / 100

        prec = self.pool.get('decimal.precision').precision_get(
            cur, uid, 'Account')
        for inv in inv_obj.browse(cur, uid, context.get('active_ids'),
                                  context=context):

            if mode in 'early_payment':

                refund = inv_obj.browse(cur, uid, refund_id, context=context)
                refund_lines_brw = refund.invoice_line
                line_data_dict = {}

                if not float_compare(
                        wizard_brw.amount_total, (inv.amount_total * percent),
                        precision_digits=prec):
                    for refund_line in refund_lines_brw:
                        tax_tuple = refund_line.\
                            invoice_line_tax_id.\
                            __dict__.get('_ids')

                        price_unit_discount = refund_line.price_unit *\
                            percent * refund_line.quantity

                        if line_data_dict.get(tax_tuple):
                            line_data_dict[tax_tuple]['price_unit'] +=\
                                price_unit_discount
                        else:
                            line_data_dict[tax_tuple] =\
                                inv_line_obj.copy_data(cur,
                                                       uid,
                                                       refund_line.id)
                            line_data_dict[tax_tuple]['product_id'] =\
                                wizard_brw.product_id.id
                            line_data_dict[tax_tuple]['name'] =\
                                wizard_brw.product_id.name
                            line_data_dict[tax_tuple]['price_unit'] =\
                                price_unit_discount
                            line_data_dict[tax_tuple]['quantity'] =\
                                1

                        inv_line_obj.unlink(cur, uid, [refund_line.id])
                    for new_refund_line in line_data_dict.values():
                        inv_line_obj.create(cur,
                                            uid,
                                            new_refund_line,
                                            context=context)

                else:
                    if refund_lines_brw:
                        refund_line = refund_lines_brw[0]
                        new_refund_line =\
                            inv_line_obj.copy_data(cur, uid, refund_line.id)
                        new_refund_line['product_id'] =\
                            wizard_brw.product_id.id
                        new_refund_line['name'] =\
                            wizard_brw.product_id.name
                        new_refund_line['price_unit'] =\
                            wizard_brw.amount_total
                        new_refund_line['quantity'] =\
                            1
                        new_refund_line['invoice_line_tax_id'] =\
                            False

                        for refund_line in refund_lines_brw:
                            inv_line_obj.unlink(cur, uid, [refund_line.id])

                        inv_line_obj.create(cur,
                                            uid,
                                            new_refund_line,
                                            context=context)

                refund.button_reset_taxes()
                movelines = inv.move_id.line_id
                to_reconcile_ids = {}
                for line in movelines:
                    if line.account_id.reconcile and not line.reconcile_id:
                        to_reconcile_ids.setdefault(line.account_id.id,
                                                    []).append(line.id)
                refund.signal_workflow('invoice_open')
                refund = inv_obj.browse(cur, uid, refund_id[0],
                                        context=context)
                for tmpline in refund.move_id.line_id:
                    if tmpline.account_id.reconcile:
                        to_reconcile_ids[tmpline.
                                         account_id.id].append(tmpline.id)
                for account in to_reconcile_ids:
                    if len(to_reconcile_ids[account]) > 1:
                        account_m_line_obj.reconcile_partial(
                            cur, uid, to_reconcile_ids[account],
                            context=context)
        return result

    def _get_percent_default(self, cur, uid, ids, context=None):
        """
        It is a hook method. In order to put some smart computation.
        """
        if context is None:
            context = {}
        return 5.0

    _defaults = {
        'product_id': lambda self, cur,
        uid, c: self._search_xml_id(cur,
                                    uid,
                                    'account_refund_early_payment',
                                    'product_discount_early_payment',
                                    context=c),
        'percent': _get_percent_default,

    }
