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
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
        date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice,self).onchange_partner_id(cr, uid, ids, type, partner_id,\
        date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if partner_id:
            partner_invoice_description=self.pool.get('res.partner').browse(cr,uid,partner_id).description_invoice
            res['value'].update({'comment':partner_invoice_description})
        return res

account_invoice()
