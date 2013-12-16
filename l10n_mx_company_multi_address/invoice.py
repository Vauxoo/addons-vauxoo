# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
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


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_address_issued_invoice(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(
                cr, uid, journal_id, context=context)
            a = data_journal.address_invoice_company_id and \
                data_journal.address_invoice_company_id.id or False
            b = data_journal.company2_id and \
            data_journal.company2_id.address_invoice_parent_company_id and \
            data_journal.company2_id.address_invoice_parent_company_id.id or False
            c = data.company_id and \
            data.company_id.address_invoice_parent_company_id and \
            data.company_id.address_invoice_parent_company_id.id or False
            address_invoice = a or b or c or False
            res[data.id] = address_invoice
        return res

    def _get_company_emitter_invoice(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(
                cr, uid, journal_id, context=context)
            company_invoice = data_journal.company2_id and \
                data_journal.company2_id.id or data.company_id and \
                data.company_id.id or False
            res[data.id] = company_invoice
        return res

    _columns = {
        'address_issued_id': fields.function(_get_address_issued_invoice,
            type="many2one", relation='res.partner', string='Address Issued \
            Invoice', help='This address will be used as address that issued \
            for electronic invoice'),
        'company_emitter_id': fields.function(_get_company_emitter_invoice,
            type="many2one", relation='res.company', string='Company Emitter \
            Invoice', help='This company will be used as emitter company in \
            the electronic invoice')
    }

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        if context is None:
            context = {}
        result = super(account_invoice, self).onchange_journal_id(
            cr, uid, ids, journal_id, context=context)
        address_id = journal_id and self.pool.get('account.journal').browse(
            cr, uid, journal_id, context=context) or False
        if address_id and address_id.address_invoice_company_id:
            result['value'].update({'address_invoice_company_id': 
                                    address_id.address_invoice_company_id.id})
        if address_id and address_id.company2_id:
            result['value'].update({'company2_id': address_id.company2_id.id})
        return result
