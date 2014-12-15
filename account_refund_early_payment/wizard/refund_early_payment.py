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

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression

from openerp.addons.account.wizard import account_invoice_refund as air

class account_invoice_refund(osv.osv_memory):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    filter_refund = \
        air.account_invoice_refund._columns.get('filter_refund').__dict__
    REFUND_METHOD = filter_refund.get('selection')
    REFUND_METHOD.append(('early_payment',
                         'Early payment: Discount early payment'))

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

