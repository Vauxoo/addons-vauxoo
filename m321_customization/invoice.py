# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import fields, osv

import decimal_precision as dp


class inherited_invoice(osv.Model):
    """
    M321 Customizations for account.invoice model
    """
    _inherit = "account.invoice"
    _columns = {
        'profit_code': fields.integer("Code from profit",
            help="Invoice code from profit"),
    }


class inherited_invoice_line(osv.Model):
    _inherit = "account.invoice.line"
    _columns = {
        'net_discount': fields.float('Net Discount', required=False,
        digits_compute=dp.get_precision('Account'),
        help="""Loaded from data imported from Profit is equal to sale price
            minus real sold price"""),
        'discount_code_profit': fields.char('Discount code from profit',
            size=7)
    }

    _defaults = {
        'net_discount': 0.0
    }
