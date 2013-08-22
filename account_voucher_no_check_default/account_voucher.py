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
from openerp.osv import fields, osv

class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id,\
        amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids,\
            partner_id, journal_id, amount, currency_id, ttype, date,\
            context=context)
        values = res.get('value', False)
        if values and values.get('line_cr_ids') and ttype == 'payment':
            for line in values.get('line_cr_ids'):
                line.update({'reconcile' : False})
        if values and values.get('line_dr_ids') and ttype == 'receipt':
            for line in values.get('line_dr_ids'):
                line.update({'reconcile' : False})
        return res
    
