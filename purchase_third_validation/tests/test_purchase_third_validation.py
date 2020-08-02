from odoo.tests import Form, TransactionCase


class TestPurchaseThirdValidation(TransactionCase):
    """This Tests validate that purchase order need a third validation
    when the amount total is over the limit assigned
    """

    def setUp(self):
        super(TestPurchaseThirdValidation, self).setUp()

        self.vendor = self.env.ref('base.res_partner_1')
        self.company = self.env.ref('base.main_company')
        self.product = self.env.ref('product.product_product_9')
        self.group_purchase_manager = self.env.ref('purchase.group_purchase_manager')
        self.group_purchase_validate = self.env.ref(
            'purchase_third_validation.general_purchase_manager')
        self.user_purchase = self.env['res.users'].with_context(no_reset_password=False).create({
            'name': 'Purchase Test',
            'login': 'purchase@example.com',
            'email': 'purchase@example.com',
            'groups_id': [(6, 0, [
                self.group_purchase_manager.id,
                self.group_purchase_validate.id,
            ])],
        })
        self.company.po_double_validation = 'three_step'
        self.uid = self.user_purchase

    def create_purchase_order(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.vendor
        purchase_order = Form(self.env['purchase.order'])
        purchase_order.partner_id = partner
        purchase_order = purchase_order.save()
        self.create_po_line(purchase_order, **line_kwargs)
        return purchase_order

    def create_po_line(self, purchase_order, product=None, quantity=1, price=100):
        if product is None:
            product = self.product
        with Form(purchase_order) as po:
            with po.order_line.new() as line:
                line.product_id = product
                line.product_qty = quantity
                line.price_unit = price

    def _test_01_purchase_by_1000(self):
        """Test with the amount of purchase order by a total less than minimum
        required to not need a second validation, (amount = 1000).
        """
        po = self.create_purchase_order(price=100)
        po.button_confirm()
        self.assertEqual(po.state, 'purchase', 'Purchase Order should be confirmed')

    def _test_02_purchase_by_5000(self):
        """Test with the amount of purchase order by a total higher than the
        minimum required to need a second validation, but not need a third,
         (amount = 5000).
        """
        po = self.create_purchase_order(price=5000)
        po.button_confirm()
        self.assertEqual(po.state, 'purchase', 'Purchase Order should be confirmed')

    def test_03_purchase_by_100000(self):
        """Test with the amount of purchase order by a total higher than the
         minimum required to need a third validation, (amount = 100000).
        """
        po = self.create_purchase_order(price=100000)
        po.button_confirm()
        self.assertEqual(po.state, 'purchase', 'Purchase Order should be confirmed')

        self.user_purchase.groups_id -= self.group_purchase_validate
        po2 = self.create_purchase_order(price=100000)
        po2.button_confirm()
        self.assertEqual(
            po2.state, 'third approve',
            'Purchase Order should be waiting for third validation')
