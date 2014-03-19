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
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class inherits_sale(osv.Model):
    
    '''Inherit sale order to add a new field, Payment Terms'''
    
    _inherit = 'sale.order'
    
    _columns = {

        'acc_payment': fields.many2one('res.partner.bank', 'Account Number',
            readonly=True, states={'draft': [('readonly', False)]}, help='Is \
            the account with which the client pays the invoice, if not know \
            which account will used for pay leave empty and the XML will show \
            "Unidentified".'),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]},
            help='Indicates the way it was paid or will be paid the invoice, \
            where the options could be: check, bank transfer, reservoir in \
            account bank, credit card, cash etc. If not know as will be paid \
            the invoice, leave empty and the XML show “Unidentified”.'),
            }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):            
        '''Overwrite this method to send the payment term new to invoice '''
        if context is None:
            context = {}
        res = super(inherits_sale,self)._prepare_invoice(cr, uid, order,
                                                         lines, context)
        res.update({'pay_method_id':order.pay_method_id and\
                                        order.pay_method_id.id or False,
                    'acc_payment':order.acc_payment and\
                                        order.acc_payment.id or False,
        })

        return res 


    def onchange_partner_id(self, cr, uid, ids, part, context=None):                

        '''Overwrite this method to set payment term new to sale order '''
        if context is None:
            context = {}
        res = super(inherits_sale,self).onchange_partner_id(cr, uid, ids,
                                                            part, context)
        if part:
            part = self.pool.get('res.partner').browse(cr, uid, part, context)
            part = self.pool.get('res.partner')._find_accounting_partner(part)

            payment_term = part.pay_method_id and part.pay_method_id.id or False
            partner_bank_obj = self.pool.get('res.partner.bank')
            bank_partner_id = partner_bank_obj.search(
                                            cr, uid,
                                            [('partner_id', '=', part.id)])
            res.get('value',{}).update({                                                                     
                'pay_method_id': payment_term,                                           
                'acc_payment': bank_partner_id and bank_partner_id[0] or False,
            })                                                                           

        return res 
