from openerp.addons.account_tax_importation.tests.common import TestTaxCommon


class TestInvoiceStatementBroker(TestTaxCommon):
    """
    This test is to check that when I create a invoice to 'Reposicion de
    gastos' this invoice not create 'Iva efectivamente pagado' to this invoice,
    only to invoice that send me the broker from mi supplier.
    """

    def setUp(self):
        super(TestInvoiceStatementBroker, self).setUp()

    def test_programmatic_tax(self):
        """
        This method test the feature with bank.statement
        """
        cr, uid = self.cr, self.uid
        # I create the invoice to broker
        context = {'default_type': 'in_invoice'}
        inv_id = self.inv_model.create(cr, uid, dict(
            account_id=self.account_inv,
            partner_id=self.partner_id,
            check_total=7694.20,
            company_id=self.company_id,
            journal_id=self.journal_inv_id,
            reference_type='none',
            invoice_line=[(0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1000.0,
                'product_id': self.prod_line1,
                'quantity': 0,
                'invoice_line_tax_id': [(6, 0, [self.tax_brok16_id])],
                'invoice_broker_id': self.tax_inv_2_id
            }), (0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1299.0,
                'product_id': self.prod_line2,
                'quantity': 5,
                'invoice_line_tax_id': [(6, 0, [self.tax_16_id])]
            })]
        ), context=context)

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
