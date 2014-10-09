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


class inherits_purchase(osv.Model):

    '''Inherit purchase model to add opration cobol reference'''

    _inherit = 'purchase.order'

    _columns = {

        'payment_terms_id': fields.many2one('payment.terms.partner',
                                            'Payment Terms',
                                            help='Select the payment term '
                                            'agreed by company for '
                                            'this partner'),
    }

    def action_invoice_create(self, cr, uid, ids, context=None):
        """ Set payment termn in the new invoice create from purchase order
        """
        res = super(inherits_purchase, self).action_invoice_create(cr, uid,
                                                                  ids, context)
        inv_obj = self.pool.get('account.invoice')
        for order in self.browse(cr, uid, ids, context=context):
            inv_obj.write(cr, uid, res,
                          {'payment_terms_id': order.payment_terms_id and
                           order.payment_terms_id.id},
                          context=context)

        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        '''Set of new payment term in purchase order from partner'''
        partner = self.pool.get('res.partner')
        res = super(inherits_purchase, self).onchange_partner_id(cr, uid, ids,
                                                                partner_id)

        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
            }}
        supplier = partner.browse(cr, uid, partner_id)
        print 'aa', supplier.property_payment_term_p_suppliers
        res.get('value', {}).update({
            'payment_terms_id': supplier.property_payment_term_p_suppliers and
            supplier.property_payment_term_p_suppliers.id or False})

        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        '''Send new payment term from purchase to picking'''
        res = super(inherits_purchase, self)._prepare_order_picking(cr, uid,
                                                                   order,
                                                                   context)
        res.update({'payment_terms_id': order.payment_terms_id and
                    order.payment_terms_id.id})
        return res
