
from odoo.tests.common import TransactionCase


class TestEarlyPayment(TransactionCase):
    def setUp(self):
        super(TestEarlyPayment, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.refund_wizard = self.env['account.invoice.refund']
        self.partner = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_5')

    def create_invoice(self, inv_type='out_invoice', product=None):
        invoice = self.invoice_model.create({
            'partner_id': self.partner.id,
            'type': inv_type,
        })
        self.create_invoice_line(invoice, product)
        return invoice

    def create_invoice_line(self, invoice, product=None):
        if product is None:
            product = self.product
        line = self.invoice_line_model.new({
            'product_id': product.id,
            'invoice_id': invoice.id,
            'quantity': 1,
        })
        line._onchange_product_id()
        values = line._convert_to_write(line._cache)
        return self.invoice_line_model.create(values)

    def test_01_early_payment_from_invoices(self):
        """Test case: apply early payment refund to invoices

        This test covers the process of applying an early payment discount to
        several invoices.
        """
        # Create three invoices for different products
        product2 = self.env.ref('product.product_product_6')
        product3 = self.env.ref('product.product_product_7')
        invoices = (self.create_invoice(product=self.product)
                    + self.create_invoice(product=product2)
                    + self.create_invoice(product=product3))

        invoices.action_invoice_open()
        self.assertEqual(invoices.mapped('state'), 3*['open'])

        # Create the refund
        ctx = {'active_model': 'account.invoice', 'active_ids': invoices.ids}
        wizard = self.refund_wizard.with_context(ctx).create({
            'filter_refund': 'early_payment',
            'percentage': 5.0,
            'description': 'Test discount',
            'date': invoices[0].date,
            'date_invoice': invoices[0].date_invoice,
        })
        wizard._onchange_amount_total()
        result = wizard.invoice_refund()
        self.assertTrue(result)

        # Check created refunds
        refunds = self.invoice_model.search(result['domain'], order='id')
        self.assertEqual(len(refunds), 3)
        self.assertListEqual(
            refunds.mapped('origin'), invoices.mapped('number'))

        # Refunds should be for 5% of invoice totals
        five_percent = [x*5/100 for x in invoices.mapped('amount_total')]
        self.assertEqual(refunds.mapped('amount_total'), five_percent)
