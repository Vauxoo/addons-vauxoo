# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty ofres.partner form

#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False):
        res = super(
            account_invoice, self).onchange_partner_id(cr, uid, ids, type,
                    partner_id, date_invoice=date_invoice,
                    payment_term=payment_term, partner_bank_id=partner_bank_id,
                    company_id=company_id)
        if partner_id:
            partner_invoice_description = self.pool.get(
                'res.partner').browse(cr, uid, partner_id).description_invoice
            res['value'].update({'comment': partner_invoice_description})
        return res


class stock_invoice_onshipping(osv.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    def create_invoice(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        res = super(stock_invoice_onshipping, self).create_invoice(
            cr, uid, ids, context=context)
        invoice_ids = context['active_ids']
        for invoice_id in invoice_ids:
            invoice_description = self.pool.get('account.invoice').browse(
                cr, uid, res[invoice_id]).partner_id.description_invoice
            if invoice_description:
                self.pool.get('account.invoice').write(cr, uid, res[
                                invoice_id], {'comment': invoice_description})
        return res


class sale_make_invoice(osv.TransientModel):
    _inherit = 'sale.make.invoice'

    def make_invoices(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        res = super(sale_make_invoice, self).make_invoices(
            cr, uid, ids, context=context)
        id_invoice = eval(res['domain'])
        ids_invoices = id_invoice[0][2]
        for invoice_id in ids_invoices:
            invoice_description = self.pool.get('account.invoice').browse(
                cr, uid, invoice_id).partner_id.description_invoice
            if invoice_description:
                self.pool.get('account.invoice').write(
                    cr, uid, invoice_id, {'comment': invoice_description})
        return res


class sale_order(osv.Model):
    _inherit = 'sale.order'

    def action_invoice_create(self, cr, uid, ids, grouped=False,
                                states=['confirmed', 'done', 'exception'],
                                date_inv=False, context=None):
        if not context:
            context = {}
        res = super(sale_order, self).action_invoice_create(cr, uid, ids,
                    grouped=False, states=['confirmed', 'done', 'exception'],
                    date_inv=date_inv, context=context)
        invoice_description = self.pool.get('account.invoice').browse(
            cr, uid, res).partner_id.description_invoice
        if invoice_description:
            self.pool.get('account.invoice').write(
                cr, uid, res, {'comment': invoice_description})
        return res
