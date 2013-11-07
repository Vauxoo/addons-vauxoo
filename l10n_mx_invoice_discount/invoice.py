# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc, release

import time
from xml.dom import minidom
import os
import base64
import hashlib
import tempfile
import os
import codecs
from datetime import datetime
import decimal_precision as dp


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_data_parents = super(account_invoice, self).\
        _get_facturae_invoice_dict_data(cr, uid, ids, context)
        invoice = self.browse(cr, uid, ids)[0]
        sub_tot = 0
        for line in invoice.invoice_line:
            sub_tot += line.price_unit * line.quantity
            invoice_data_parents[0]['Comprobante']['Conceptos'][
                invoice.invoice_line.index(line)]['Concepto']\
                ['cantidad'] = line.quantity or '0.0'
            invoice_data_parents[0]['Comprobante']['Conceptos']\
                [invoice.invoice_line.index(line)]['Concepto']\
                ['descripcion'] = line.name or ' '
            invoice_data_parents[0]['Comprobante']['Conceptos']\
                [invoice.invoice_line.index(line)]['Concepto']\
                ['importe'] = line.price_unit * line.quantity or '0'
            invoice_data_parents[0]['Comprobante']['Conceptos']\
                [invoice.invoice_line.index(line)]['Concepto']\
                ['noIdentificacion'] = line.product_id.default_code or '-'
            invoice_data_parents[0]['Comprobante']['Conceptos']\
                [invoice.invoice_line.index(line)]['Concepto']\
                ['unidad'] = line.uos_id and line.uos_id.name or ''
            invoice_data_parents[0]['Comprobante']['Conceptos']\
                [invoice.invoice_line.index(line)]['Concepto']\
                ['valorUnitario'] = line.price_unit or '0'

        invoice_data_parents[0]['Comprobante'][
            'motivoDescuento'] = invoice.motive_discount or ''
        invoice_data_parents[0]['Comprobante']['descuento'] = invoice.\
            global_discount_amount and '%.3f' % invoice.global_discount_amount or '0'
        invoice_data_parents[0]['Comprobante']['subTotal'] = sub_tot
        return invoice_data_parents

    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        invoice_line_obj = self.pool.get('account.invoice.line')
        disc_amount_line = 0
        if inv.global_discount_percent != 0:
            for line in inv.invoice_line:
                disc_amount_line += line.price_unit * \
                    line.quantity * (inv.global_discount_percent/100 or 1)
            disc_line = float('%.3f' % disc_amount_line)
            disc_ammount = float('%.3f' % inv.global_discount_amount)
            if disc_line != disc_ammount:
                raise osv.except_osv(_('Warning !'), _(
                    'Global Discount Amount was changed!\nClick on compute to update tax base'))
            super(account_invoice, self).check_tax_lines(
                cr, uid, inv, compute_taxes, ait_obj)

    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = self.browse(cr, uid, ids)[0]
        invoice_line_obj = self.pool.get('account.invoice.line')
        sub_tot = 0
        for line in invoice.invoice_line:
            discount_dic = {
                'discount': invoice.global_discount_percent,
            }
            sub_tot += line.price_unit * line.quantity
            invoice_line_obj.write(cr, uid, [line.id], discount_dic)

        discount = invoice.global_discount_percent and sub_tot * (
            invoice.global_discount_percent and invoice.\
            global_discount_percent/100 or 1) or '0'
        self.write(cr, uid, ids, {'global_discount_amount': discount,
                   'global_discount_percent': invoice.global_discount_percent})
        super(account_invoice, self).button_reset_taxes(
            cr, uid, ids, context=context)
        return True

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
        date_invoice=False, payment_term=False, partner_bank_id=False,
        company_id=False):
        res = super(account_invoice, self).onchange_partner_id(cr, uid, ids,
            type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        partner_obj = self.pool.get('res.partner')
        if partner_id:
            partner_brw = partner_obj.browse(cr, uid, partner_id)

        res['value']['global_discount_percent'] = partner_id and \
            partner_brw.discount or False
        res['value']['motive_discount'] = partner_id and \
            partner_brw.motive_discount or False
        return res

    _columns = {
        'global_discount_amount': fields.float('Global Discount Amount',
            readonly=True),
        'global_discount_percent': fields.float('Global Discount Percent',
            readonly=True, states={'draft': [('readonly', False)]}),
        'motive_discount': fields.char('Motive Discount', size=128,
            readonly=True, states={'draft': [('readonly', False)]}),
    }


class account_invoice_line(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision(
            'Account'), readonly=True),
    }
