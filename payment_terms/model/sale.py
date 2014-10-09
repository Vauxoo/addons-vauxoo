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
from openerp.osv import osv, fields


class inherits_sale(osv.Model):

    '''Inherit sale order to add a new field, Payment Terms'''

    _inherit = 'sale.order'

    _columns = {

        'payment_terms_id': fields.many2one('payment.terms.partner',
                                            'Payment Terms',
                                            help='Select the payment term '
                                            'agreed by company for '
                                            'this partner'),
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        '''Overwrite this method to send the payment term new to invoice '''

        res = super(inherits_sale, self)._prepare_invoice(cr, uid, order,
                                                         lines, context)
        res.update({'payment_terms_id': order.payment_terms_id and
                    order.payment_terms_id.id
                    })

        return res

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        '''Overwrite this method to set payment term new to sale order '''

        res = super(inherits_sale, self).onchange_partner_id(cr, uid, ids,
                                                            part, context)
        part = self.pool.get('res.partner').browse(cr, uid, part, context)

        payment_term = part.property_payment_term_p_customer and\
            part.property_payment_term_p_customer.id or False
        res.get('value', {}).update({
            'payment_terms_id': payment_term,
        })

        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        '''Overwrite this method to send the payment term new to picking '''

        res = super(inherits_sale, self)._prepare_order_picking(cr, uid,
                                                               order,
                                                               context)
        res.update({'payment_terms_id': order.payment_terms_id and
                    order.payment_terms_id.id})
        return res
