from odoo.tests import Form, TransactionCase


class TestMrpResponsible(TransactionCase):

    def setUp(self):
        super(TestMrpResponsible, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.product_mrp = self.env.ref("product.product_product_3")
        # Creating User
        self.user_responsible = self.env['res.users'].with_context(no_reset_password=False).create({
            'name': 'Product Responsible Test',
            'login': 'product@example.com',
            'email': 'product@example.com',
        })
        self.product_mrp.production_responsible = self.user_responsible

    def create_manufacturing_order(self, product=None):
        if product is None:
            product = self.product_mrp
        mo = Form(self.env['mrp.production'])
        mo.product_id = product
        return mo.save()

    def test_01_create_product(self):
        # Creating manufacturing order
        mo = self.create_manufacturing_order()
        self.assertEqual(
            mo.user_id, self.user_responsible,
            'The Responsible was not set correctly')

    def test_02_responsible_from_procurement_mrp(self):
        """This test validate responsible user is set in MO when is created from Procurement"""
        procurement = self.env['procurement.group'].create({'name': 'Test'})
        existing_mos = self.env['mrp.production'].search([('product_id', '=', self.product_mrp.id)])
        procurement.run(
            product_id=self.product_mrp,
            product_qty=1,
            product_uom=self.product_mrp.uom_id,
            location_id=self.location_stock,
            name='Test procurement',
            origin=procurement.name,
            values={})

        created_mo = self.env['mrp.production'].search([
            ('product_id', '=', self.product_mrp.id),
            ('id', 'not in', existing_mos.ids),
        ])

        self.assertEqual(len(created_mo), 1)
        self.assertEqual(
            created_mo.user_id, self.user_responsible,
            'The Responsible was not set correctly')
