# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2012-TODAY OpenERP S.A. <http://openerp.com>
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

from openerp.tests.common import TransactionCase


class TestEarlyPayment(TransactionCase):
    def setUp(self):
        super(TestEarlyPayment, self).setUp()
        self.account_receivable_id = self.env.ref("account.a_recv")
        self.account_invoice_model = self.env['account.invoice']
        self.account_invoice_line_model = self.env['account.invoice.line']
        self.account_invoice_refund_model = self.env['account.invoice.refund']

    def test_early_payment_from_invoices(self):
        """
            This test validate the split of reconciliatio between
            one refund and invoices to apply early payment refund
        """
        move_line_id = []
        invoice_ids = []
        invoice_number = []

        # get all invoices demo to use to reconcile with refund
        invoice_brw_ids = [
            self.env.ref(
                'account_refund_early_payment.invoice_%s' % invoice_number_id)
            for invoice_number_id in [1, 2, 3, 4, 5, 6]]

        for invoice_id in invoice_brw_ids:
            # save invoice ids to use in active_ids of wizard of early_payment
            invoice_ids.append(invoice_id.id)
            # validate invoice
            invoice_id.signal_workflow('invoice_open')
            invoice_number.append(invoice_id.number)

            # we search aml with account receivable
            for line_invoice in invoice_id.move_id.line_id:
                if line_invoice.account_id.id == self.account_receivable_id.id:
                    move_line_id.append(line_invoice)
                    break
        # create refund early payment
        account_refund_id = self.account_invoice_refund_model.with_context(
            {'active_ids': invoice_ids}).create({
                'filter_refund': 'early_payment',
                'amount_total': '52.61'
            })
        # it is necessary to allow cancel entry because after reconciliation
        # normal we need to modify and split journal entry original
        account_refund_id.journal_id.write({'update_posted': True})
        result = account_refund_id.invoice_refund()
        refund_id = result.get('domain')[1][2]
        checked_line_reconciled = []
        checked_line = 0
        refund_brw = self.account_invoice_model.browse(refund_id)
        for line_move_refund_id in refund_brw.move_id.line_id:
            for line_move_invoice_id in move_line_id:
                if line_move_refund_id.reconcile_partial_id ==\
                        line_move_invoice_id.reconcile_partial_id:
                    checked_line_reconciled.append(
                        line_move_refund_id.reconcile_partial_id.id)
            if line_move_refund_id.credit == 5.01:
                checked_line += 1
            if line_move_refund_id.credit == 16.00:
                checked_line += 1
            if line_move_refund_id.credit == 20.00:
                checked_line += 1
            if line_move_refund_id.credit == 0.05:
                checked_line += 1
            if line_move_refund_id.credit == 1.52:
                checked_line += 1
            if line_move_refund_id.credit == 10.03:
                checked_line += 1

        self.assertEquals(checked_line, 6)
        self.assertEquals(len(set(checked_line_reconciled)), 6)
        self.assertEquals(
            refund_brw.origin,
            ','.join(inv_number for inv_number in invoice_number))
