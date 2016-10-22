# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase


class TestUpdateRecursiveStandardPrice(TransactionCase):

    def setUp(self):
        super(TestUpdateRecursiveStandardPrice, self).setUp()
        self.prod_obj = self.env['product.product']
        self.mrp_obj = self.env['mrp.bom']
        self.wizard_obj = self.env['wizard.price']

    def test_001_verify_cost_updated(self):
        """Verify that products in average or real cost methods is not updated
        the standard price with the cron."""
        products = self.generate_structure()
        ctx = {'active_id': products[0].id}
        wiz = self.wizard_obj.with_context(ctx).create({})
        wiz.with_context({}).execute_cron(products[0].ids)
        self.assertEquals(
            products[0].standard_price, 115.0,
            'Standard price to main product must be 115.0, and is different')
        self.assertEquals(
            products[1].standard_price, 20.0,
            'This product have not mrp, and the price should not have changed')
        self.assertEquals(
            products[2].standard_price, 35.0,
            'The costing method to this product is average, the standard '
            'price should not have changed')
        self.assertEquals(
            products[3].standard_price, 45.0,
            'Standard price to this product must be 45.0, and is different')
        self.assertEquals(
            products[4].standard_price, 50.0,
            'The costing method to this product is average, the standard '
            'price should not have changed')
        self.assertEquals(
            products[5].standard_price, 30.0,
            'This product have not mrp, and the price should not have changed')
        self.assertEquals(
            products[6].standard_price, 15.0,
            'This product have not mrp, and the price should not have changed')

    def generate_structure(self):
        """Is generated the next structure of bom and product to update costs
                    Product1
                        |
            -------------------------
            |                       |
        Product 2               Product3
                                    |
                        -------------------------
                        |                       |
                    Product4                Product5
                        |
            -------------------------
            |                       |
        Product6                Product7

        Where Product3 & Product5 are setted as Average Price and the other
        products are setted as Standard Price
        """
        prod1 = self.prod_obj.create({
            'name': 'Product 1',
            'type': 'consu',
            'cost_method': 'standard',
            'standard_price': 100.0,
        })
        prod2 = self.prod_obj.create({
            'name': 'Product 2',
            'type': 'consu',
            'cost_method': 'standard',
            'standard_price': 20.0,
        })
        prod3 = self.prod_obj.create({
            'name': 'Product 4',
            'type': 'consu',
            'cost_method': 'average',
            'standard_price': 35.0,
        })
        prod4 = self.prod_obj.create({
            'name': 'Product 4',
            'type': 'consu',
            'cost_method': 'standard',
            'standard_price': 40.0,
        })
        prod5 = self.prod_obj.create({
            'name': 'Product 5',
            'type': 'consu',
            'cost_method': 'average',
            'standard_price': 50.0,
        })
        prod6 = self.prod_obj.create({
            'name': 'Product 6',
            'type': 'consu',
            'cost_method': 'standard',
            'standard_price': 30.0,
        })
        prod7 = self.prod_obj.create({
            'name': 'Product 7',
            'type': 'consu',
            'cost_method': 'standard',
            'standard_price': 15.0,
        })
        self.mrp_obj.create({
            'product_tmpl_id': prod1.product_tmpl_id.id,
            'product_id': prod1.id,
            'bom_line_ids': [
                (0, 0, {'product_id': prod2.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
                (0, 0, {'product_id': prod3.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
            ]
        })
        self.mrp_obj.create({
            'product_tmpl_id': prod3.product_tmpl_id.id,
            'product_id': prod3.id,
            'bom_line_ids': [
                (0, 0, {'product_id': prod4.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
                (0, 0, {'product_id': prod5.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
            ]
        })
        self.mrp_obj.create({
            'product_tmpl_id': prod4.product_tmpl_id.id,
            'product_id': prod4.id,
            'bom_line_ids': [
                (0, 0, {'product_id': prod6.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
                (0, 0, {'product_id': prod7.id,
                        'type': 'normal',
                        'product_qty': 1.0,
                        'product_efficiency': 1.0}),
            ]
        })
        return [prod1, prod2, prod3, prod4, prod5, prod6, prod7]
