# coding: utf-8
from openerp.addons.account_tax_importation.tests.common import TestTaxCommon


class TestInvoiceStatementBroker(TestTaxCommon):
    """This test is to check that when I create a invoice to 'Reposicion de
    gastos' this invoice not create 'Iva efectivamente pagado' to this invoice,
    only to invoice that send me the broker from mi supplier.
    """

    def setUp(self):
        super(TestInvoiceStatementBroker, self).setUp()

    def test_programmatic_tax_statement(self):
        """This method test the feature with bank.statement
        """
        cr, uid = self.cr, self.uid
        # I create the invoice to broker
        context = {'default_type': 'in_invoice'}
        inv_id = self.create_invoice(cr, uid, context=context)

        # I try validate the invoice
        self.inv_model.signal_workflow(cr, uid, [inv_id], 'invoice_open')

        # I check the total to invoice created
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id,
            ['amount_total']).get('amount_total', 0.0), 7694.20)

        # I check the state of invoice is open
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id, ['state']).get('state', ''), 'open')

        invoice_record = self.inv_model.browse(cr, uid, [inv_id])

        # We search aml with account payable
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_inv:
                line_id = line_invoice
                break
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_id, -7694.20,
            self.journal_vou_id)

        # I check the status to invoice == 'paid'
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id, ['state']).get('state', ''), 'paid')

        # I check the journal entry to the invoice
        move_inv = self.inv_model.browse(cr, uid, inv_id).move_id
        error = False
        for line in move_inv.line_id:
            if line.partner_id.id != self.partner_id:
                if not line.amount_base and not line.tax_id_secondary:
                    error = True
        if error:
            self.assertEquals(0, 1, "The invoice have not line to report in "
                              "DIOT to supplier broker")

        # I check the journal entry from payment
        self.assertEquals(len(move_line_ids), 4)
