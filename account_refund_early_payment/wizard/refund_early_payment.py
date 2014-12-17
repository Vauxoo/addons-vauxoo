#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
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

class account_invoice_refund(osv.osv_memory):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    filter_refund = \
        air.account_invoice_refund._columns.get('filter_refund').__dict__
    REFUND_METHOD = filter_refund.get('selection')
    REFUND_METHOD.append(('early_payment',
                         'Early payment: Discount early payment'))

    def _search_xml_id(self, cr, uid, model, record_xml_id, context=None):
        if context is None:
            context = {}
        imd_obj = self.pool.get('ir.model.data')
        res_id = False
        imd_id = imd_obj.search(cr, uid,
                                [('module', '=', model),
                                ('name', '=', record_xml_id)])
        if imd_id:
            res_id = imd_obj.browse(cr, uid, imd_id)[0].res_id
        return res_id

    _columns = {
       'filter_refund': fields.selection(REFUND_METHOD,
                                         "Refund Method",
                                         required=True,
                                         help=filter_refund.get('_args')\
                                                 .get('help') ),
       'percent' : fields.float('Percent'),
       'discount_applied' : fields.selection([('amount_total',' Amount Total'),
                                             ('balance','Balance')],
                                             'Discount applies to',
                                             help = 'Amount to be applied discount'),
       'product_id' : fields.many2one('product.product', string='Product'),
        }

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):

        inv_obj = self.pool.get('account.invoice')
        account_m_line_obj = self.pool.get('account.move.line')
        inv_line_obj = self.pool.get('account.invoice.line')

        result = super(account_invoice_refund,self).compute_refund(cr, uid,
                                                                ids, mode,
                                                                context=context)
        invoice = result.get('domain')[2][0]
        import pdb; pdb.set_trace()

        return result

    def _get_percent_default(cr, uid, ids, context=None):
        return 5.0

    _defaults = {
        'product_id': lambda self,cr,uid,c: self._search_xml_id(cr, uid,
            'account_refund_early_payment', 'product_discount_early_payment', context=c),
        'percent' : _get_percent_default,

    }

