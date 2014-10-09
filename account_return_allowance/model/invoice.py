# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Nhomar Hernandez nhomar@vauxoo.com
# Credits##########################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def config_verification(self, cr, uid):
        '''
        Verify if the in this company i must send the return and the allowance
        to a different account invoice per invoice.
        TODO: Maybe we need to make this verification per_journal and not per
        company
        '''
        company = self.pool.get('res.users').browse(
            cr, uid, [uid], context=None)[0].company_id
        acc_id = self.pool.get('res.company').browse(cr, uid, [
            company.id])[0].property_account_allowance_global.id
        acc_id_return = self.pool.get('res.company').browse(
            cr, uid, [company.id])[0].property_account_return_global.id
        return (company.make_allowance_aml, acc_id, acc_id_return)

    def get_account_aml(self, cr, uid, l):
        '''
        Get the account id to put on counter part.
        Improve this method to allow do it more smart.
        '''
        # TODO: make recursive load account from parents categ_id
        type_inv = l.invoice_id.type
        cv = self.config_verification(cr, uid)
        if cv[0]:
            p_id = l.product_id
            p_tmpl_id = p_id.product_tmpl_id
            if type_inv == 'out_invoice':
                if p_id.property_account_allowance:
                    return p_id.property_account_allowance.id
                elif p_tmpl_id.categ_id.property_account_allowance:
                    return p_tmpl_id.categ_id.property_account_allowance.id
                else:
                    return cv[1]
            if type_inv == 'out_refund':
                if p_id:
                    if p_id.property_account_return:
                        return p_id.property_account_return.id
                    elif p_tmpl_id.categ_id.property_account_return:
                        return p_tmpl_id.categ_id.property_account_return.id
                    else:
                        return cv[2]
                else:
                    # It is considered an allowance, if YES change per cv[1]
                    return cv[2]

    def get_dict_allowance(self, cr, uid, l, context=None):
        '''
        Allowance:
        Get list of lines to make the aml for allowance accounts.
        This method is experimental given this situation:
        NO Analityc analisis for this ammount.
        NO Multicurrency feature.
        Overwrite this method or propose a merge proposal to improve this
        behavior.
        '''
        acc_id = self.get_account_aml(cr, uid, l)
        amount_line = l.quantity*l.price_unit - l.price_subtotal
        if acc_id and amount_line > 1e-8:
            line = {'name': _('Discount %s' % l.name[:64]),
                    'ref': _('Discount %s' % l.name[:64]),
                    'credit': False,
                    'debit': amount_line,
                    'product_id': l.product_id.id,
                    #'amount_currency': 0, #TODO: apply multicurrency?
                    #'currency_id': False, #TODO: apply multicurrency?
                    #'tax_code_id': 21, #TODO: Apply some tax?
                    #'analytic_lines': [], #TODO: apply analityc expenses?
                    #'analytic_account_id': False,
                    # TODO: apply analityc expenses?
                    'product_uom_id': l.uos_id.id,
                    'quantity': l.quantity,
                    'partner_id': l.invoice_id.partner_id.id,
                    'account_id': acc_id}
            # TODO: Should i make a line.copy() and a line.update()?
            counter_line = {'name': _('Discount %s' % l.name[:64]),
                            'ref': _('Discount %s' % l.name[:64]),
                            'credit': amount_line,
                            'debit': False,
                            'product_id': l.product_id.id,
                            #'amount_currency': 0,
                            # TODO: apply multicurrency?
                            #'currency_id': False,
                            # TODO: apply multicurrency?
                            #'tax_code_id': 21,
                            # TODO: Apply some tax?
                            #'analytic_lines': [],
                            # TODO: apply analityc expenses?
                            #'analytic_account_id': False,
                            # TODO: apply analityc expenses?
                            'product_uom_id': l.uos_id.id,
                            'quantity': l.quantity,
                            'partner_id': l.invoice_id.partner_id.id,
                            'account_id': l.invoice_id.account_id.id}
            return [(0, 0, line), (0, 0, counter_line)]
        else:
            return []

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) ->
        move_lines
        Hook method to be overridden in additional modules to verify
        and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is
        generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines
        (as for create())
        :return: the (possibly updated) final move_lines to create for
        this invoice
        """
        context = {}
        type_inv = invoice_browse.type

        if type_inv == 'out_invoice':
            move_lines = super(account_invoice,
                               self).finalize_invoice_move_lines(
                                   cr, uid, invoice_browse, move_lines)
            for l in invoice_browse.invoice_line:
                if l.product_id and l.allowance:
                    lines = self.get_dict_allowance(
                        cr, uid, l, context=context)
                    # TODO: Here I need to correct the amount on all aml too!
                    [move_lines.append(y) for y in lines]
        elif type_inv == 'out_refund':
            tax_accounts = [
                acc_tax_id.account_id.id for acc_tax_id in invoice_browse.tax_line]
            receivable = [y for y in move_lines if y[2].get(
                'account_id') == invoice_browse.account_id.id or y[2].get('account_id') in tax_accounts]
            new = []
            # Do what returns must to doc
            # Ensure i take the correct line. No tax
            to_modify = [aml for aml in move_lines if aml[2].get('account_id')
                         not in tax_accounts]
            # It is not the receivable account
            to_modify = [aml for aml in to_modify if aml[2].get('account_id')
                         not in [invoice_browse.account_id.id]]
            for l in invoice_browse.invoice_line:
                if l.product_id:
                # If it is commercial.
                    if to_modify:
                        # Look for the new account
                        new_acc_id = self.get_account_aml(cr, uid, l)
                        # Build the new entry line
                        new_entry = to_modify.pop(0)[2].copy()
                        new_entry.update({'account_id': new_acc_id})
                        # Add the new entry to new s
                        entry = [(0, 0, new_entry)]
                        new = new+entry
                if not l.product_id:
                # If it is Allowance or it doen't have product_id in the line
                    if to_modify:
                        # Look for the new account
                        new_acc_id = self.get_account_aml(cr, uid, l)
                        # Build the new entry line
                        new_entry = to_modify.pop(0)[2].copy()
                        new_entry.update({'account_id': new_acc_id})
                        # Add the new entry to new s
                        entry = [(0, 0, new_entry)]
                        new = new+entry
            # join everything
            if new:
                # Verify What is the tax account and receivable and sum to new
                # entry
                move_lines = new + \
                    [aml for aml in move_lines if aml[2].get('account_id')
                     in [invoice_browse.account_id.id]] +\
                    [aml for aml in move_lines if aml[2].get('account_id')
                     in tax_accounts]
                print move_lines
        return move_lines


class account_invoice_line(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'allowance': fields.boolean('Allowance or Trade Discount', required=False, help='''True: The discount applied
will be considered an allowance.
False: discount on line will be considered a Trade Discount.
From an accounting point of view it will be considered in a different manner.
        '''),
    }
