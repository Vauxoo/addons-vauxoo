# coding: utf-8

from odoo.tests.common import TransactionCase


class TestPurchaseThirdValidation(TransactionCase):
    """
        This Tests validate that purchase order need a third validation
        when the amount total is over the limit assigned
    """

    def setUp(self):
        super(TestPurchaseThirdValidation, self).setUp()

        self.partner_id = self.env.ref('base.res_partner_3')
        self.company = self.env.ref('base.main_company')
        self.product = self.env.ref('product.product_product_9')
        self.pol = self.env['purchase.order.line']
        self.purchase_obj = self.env['purchase.order']
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.env.ref('purchase.group_purchase_manager').write(
            {'users': [(4, self.env.ref('base.user_root').id)]})
        self.company.write({'po_double_validation': 'three_step'})

    def _generate_confirm_po(self, price):
        self.po_id = self.purchase_obj.create({
            'partner_id': self.partner_id.id})
        self._create_pol(price)
        self.po_id.button_confirm()

    def _create_pol(self, price):
        new_pol = self.pol.new({
            'order_id': self.po_id.id,
            'product_id': self.product.id,
            'product_qty': 1})
        new_pol.onchange_product_id()
        pol_dict = new_pol._convert_to_write({
            name: new_pol[name] for name in new_pol._cache})
        pol_dict['price_unit'] = price
        self.pol.create(pol_dict)

    def test_purchase_by_1000(self):
        """
         Test with the amount of purchase order by a total less than minimum
         required to not need a second validation, (amount = 1000).
        """
        self._generate_confirm_po(1000)
        self.assertEqual(
            self.po_id.state, 'purchase',
            'Purchase Order should be confirmed')

    def test_purchase_by_5000(self):
        """
         Test with the amount of purchase order by a total higher than the
         minimum required to need a second validation, but not need a third,
         (amount = 5000).
        """
        self._generate_confirm_po(5000)
        self.assertEqual(
            self.po_id.state, 'purchase',
            'Purchase Order should be confirmed')

    def test_purchase_by_100000(self):
        """
         Test with the amount of purchase order by a total higher than the
         minimum required to need a third validation, (amount = 100000).
        """
        self._generate_confirm_po(100000)
        self.assertEqual(
            self.po_id.state, 'purchase',
            'Purchase Order should be confirmed')
        self.env.ref('purchase_third_validation.general_purchase_manager').\
            write({'users': [(5, 0, 0)]})
        self._generate_confirm_po(100000)
        self.assertEqual(
            self.po_id.state, 'third approve',
            'Purchase Order should be waiting for third validation')
