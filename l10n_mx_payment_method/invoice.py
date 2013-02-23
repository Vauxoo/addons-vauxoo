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

from osv import osv, fields
import tools
import time
from xml.dom import minidom
import os
import base64
import hashlib
import tempfile
import netsvc
import codecs
import release
from datetime import datetime

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice,self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        pay_method_id = False
        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, partner_id)
            pay_method_id = partner and partner.pay_method_id and partner.pay_method_id.id or False
        res['value']['pay_method_id'] = pay_method_id
        return res

    _columns = {
        'pay_method_id': fields.many2one('pay.method', 'Metodo de Pago', readonly=True, states={'draft':[('readonly',False)]}, help = 'Indica la forma en que se pagó o se pagará la factura, donde las opciones pueden ser: cheque, transferencia bancaria, depósito en cuenta bancaria, tarjeta de crédito, efectivo etc. Si no se sabe como va ser pagada la factura, dejarlo vacío y en el xml aparecerá “No identificado”.'),
        'acc_payment': fields.many2one ('res.partner.bank', 'Numero de cuenta', readonly=True, states={'draft':[('readonly',False)]},help = 'Es la cuenta con la que el cliente pagará la factura, si no se sabe con cual cuenta se va pagar dejarlo vacío y en el xml aparecerá "No identificado".'),
    }
account_invoice()
