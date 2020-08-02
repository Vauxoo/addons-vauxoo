from odoo.tests import Form, TransactionCase


class TestEarlyPayment(TransactionCase):
    def setUp(self):
        super(TestEarlyPayment, self).setUp()
        self.customer = self.env.ref('base.res_partner_3')
        self.product1 = self.env.ref('product.product_product_5')
        self.product2 = self.env.ref('product.product_product_6')
        self.product3 = self.env.ref('product.product_product_7')
        self.product_discount = self.env.ref('account_refund_early_payment.product_discount')
        self.product_discount.taxes_id = False
        self.env.user.company_id.account_sale_tax_id = False

    def create_invoice(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.customer
        invoice = Form(self.env['account.invoice'])
        invoice.partner_id = partner
        invoice = invoice.save()
        self.create_inv_line(invoice, **line_kwargs)
        return invoice

    def create_inv_line(self, invoice, product=None, quantity=1, price=150):
        if product is None:
            product = self.product1
        with Form(invoice) as inv:
            with inv.invoice_line_ids.new() as line:
                line.product_id = product
                line.quantity = quantity
                line.price_unit = price

    def create_refunds(self, invoices, percentage=5.0):
        ctx = {'active_model': invoices._name, 'active_ids': invoices.ids}
        wizard = Form(self.env['account.invoice.refund'].with_context(**ctx))
        wizard.filter_refund = 'early_payment'
        wizard.percentage = percentage
        wizard.description = 'Test discount'
        wizard = wizard.save()
        result = wizard.invoice_refund()
        self.assertTrue(result)
        refunds = self.env['account.invoice'].search(result['domain'], order='id')
        return refunds

    def test_01_early_payment_from_invoices(self):
        """Test case: apply early payment refund to invoices

        This test covers the process of applying an early payment discount to
        several invoices.
        """
        # Create three invoices for different products
        invoices = (self.create_invoice(product=self.product1, price=100)
                    + self.create_invoice(product=self.product2, price=200)
                    + self.create_invoice(product=self.product3, price=300))

        invoices.action_invoice_open()
        self.assertEqual(invoices.mapped('state'), 3*['open'])

        # Create refunds
        refunds = self.create_refunds(invoices)
        self.assertEqual(len(refunds), 3)
        self.assertListEqual(
            refunds.mapped('origin'), invoices.mapped('number'))

        # Refunds should be for 5% of invoice totals
        self.assertEqual(refunds.mapped('amount_total'), [5.0, 10.0, 15.0])
