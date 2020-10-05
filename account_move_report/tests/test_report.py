from odoo.tests import Form, TransactionCase


class TestReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.customer = self.env.ref('base.res_partner_3')
        self.product1 = self.env.ref('product.product_product_5')
        self.move_report = self.env.ref('account_move_report.template_account_move_report')

    def create_invoice(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.customer
        invoice = Form(self.env['account.move'].with_context(default_move_type='out_invoice'))
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

    def test_01_render_report(self):
        invoice = self.create_invoice()
        report_result = self.move_report._render(invoice.ids)
        self.assertEqual(len(report_result), 2)
