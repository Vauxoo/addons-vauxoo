from odoo.tests import Form
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestEarlyPayment(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        self.customer = self.env.ref('base.res_partner_3')
        self.product1 = self.env.ref('product.product_product_5')
        self.product2 = self.env.ref('product.product_product_6')
        self.product3 = self.env.ref('product.product_product_7')
        self.product_discount = self.env.ref('account_refund_early_payment.product_discount')
        self.product_discount.taxes_id = False
        self.env.user.company_id.account_sale_tax_id = False

    def create_invoice_with_product(self, product=None, move_type='out_invoice', partner=None, quantity=1, price=150):
        move_form = Form(self.env['account.move'].with_context(default_move_type=move_type))
        move_form.partner_id = partner or self.customer
        product = product or self.product1

        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.quantity = quantity
            line_form.price_unit = price

        rslt = move_form.save()
        rslt.action_post()
        return rslt

    def create_refunds(self, invoices, percentage=5.0):
        ctx = {'active_model': invoices._name, 'active_ids': invoices.ids}
        wizard = Form(self.env['account.move.reversal'].with_context(**ctx))
        wizard.refund_method = 'early_payment'
        wizard.percentage = percentage
        wizard = wizard.save()
        result = wizard.reverse_moves()
        self.assertTrue(result)
        refunds = self.env['account.move'].search(result['domain'], order='id')
        return refunds

    def test_01_early_payment_from_invoices(self):
        """Test case: apply early payment refund to invoices

        This test covers the process of applying an early payment discount to
        several invoices.
        """
        # Create three invoices for different products
        invoices = (self.create_invoice_with_product(product=self.product1, price=100)
                    + self.create_invoice_with_product(product=self.product2, price=200)
                    + self.create_invoice_with_product(product=self.product3, price=300))

        self.assertEqual(invoices.mapped('state'), 3*['posted'])

        # Create refunds
        refunds = self.create_refunds(invoices)
        self.assertEqual(len(refunds), 3)
        self.assertListEqual(
            refunds.mapped('origin'), invoices.mapped('number'))

        # Refunds should be for 5% of invoice totals
        self.assertEqual(refunds.mapped('amount_total'), [5.0, 10.0, 15.0])
