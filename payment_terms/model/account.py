# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields


class account_invoice(osv.Model):

    _inherit = 'account.invoice'

    _columns = {
        'payment_terms_id': fields.many2one('payment.terms.partner',
                                            'Payment Terms',
                                            help='Select the payment term '
                                            'agreed by company for '
                                            'this partner'),
    }


class payments_term_partner(osv.Model):

    '''Payments terms agreed by company to define how to will
       pay each partner'''

    _name = 'payment.terms.partner'

    _columns = {
        'name': fields.char('Name', 50,
                            help='Name to identify payment term'),


    }
