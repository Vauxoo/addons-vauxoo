# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
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
'''
File to add functionalitity in account.invoice.line to get the amount without
discount and the value of the discount
'''
from openerp.osv import osv, fields


class account_invoice_line(osv.osv):

    '''
    Inherit from account.invoice.line to get by line the amount without
    discount and the amount of this
    '''
    _inherit = 'account.invoice.line'

    def _get_subtotal_without_discount(self, cr, uid, ids, args, field_name,
                                       context=None):
        '''
        Method to get the subtotal of the amount without discount
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param field_name: field that call the method
        @param arg: Extra arguments
        @param context: A standard dictionary
        @return : Dict with values
        '''
        context = context or {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.quantity * line.price_unit)
        return res

    def _get_discount(self, cr, uid, ids, args, field_name, context=None):
        '''
        Method to get the amount of discount, is used subtraction by rounding
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param field_name: field that call the method
        @param arg: Extra arguments
        @param context: A standard dictionary
        @return : Dict with values
        '''
        context = context or {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.discount * line.subtotal_wo_discount / 100
        return res

    _columns = {
        'subtotal_wo_discount': fields.function(_get_subtotal_without_discount,
                                                string='SubTotal w/o Discount',
                                                store=True, type='float',
                                                help='Amount without apply \
                                                the discount of the line, is \
                                                calculated as Qty * Price Unit'
                                                ),
        'discount_amount': fields.function(_get_discount,
                                           string='Discount Amount',
                                           store=False, type='float',
                                           help='Amount total of the discount,\
                                           is calculated as Discount * \
                                           SubTotal w/o Discount / 100.'),
    }


class account_invoice(osv.osv):
    
    '''
    Inherit from account.invoice to get the amount total without discount and
    the amount total of this, of all invoice lines.
    '''
    _inherit = 'account.invoice'

    def _get_subtotal_without_discount(self, cr, uid, ids, args, field_name,
                                       context=None):
        '''
        Method to get the subtotal of the amount without discount of the sum of
        invoice lines.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param field_name: field that call the method
        @param arg: Extra arguments
        @param context: A standard dictionary
        @return : Dict with values
        '''
        context = context or {}
        total = 0.0
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.invoice_line:
                total += line.subtotal_wo_discount
            res[inv.id] = total
        return res

    def _get_discount(self, cr, uid, ids, args, field_name, context=None):
        '''
        Method to get the amount total of discount in the invoice lines.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param field_name: field that call the method
        @param arg: Extra arguments
        @param context: A standard dictionary
        @return : Dict with values
        '''
        context = context or {}
        total = 0.0
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.invoice_line:
                total += line.discount_amount
            res[inv.id] = total
        return res

    _columns = {
        'subtotal_wo_discount': fields.function(_get_subtotal_without_discount,
                                                string='SubTotal w/o Discount',
                                                store=True, type='float',
                                                help='Amount without apply the\
                                                 discount of the lines of the \
                                                invoice.'),
        'discount_amount': fields.function(_get_discount, string='Discount',
                                           store=False, type='float',
                                           help='Total of discount apply in \
                                           each line of the invoice.'),
    }
    
