# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
############################################################################

from openerp.tests.common import TransactionCase


class TestCategoryHasProducts(TransactionCase):

    def setUp(self):
        super(TestCategoryHasProducts, self).setUp()
        self.product_obj = self.env['product.product']
        self.p_category_obj = self.env['product.public.category']
        self.category_graphics = self.env.ref('product.graphics_card')

    def test_01_has_products_ok(self):
        """This test validate the fiel has_products_ok in
            product.public.category
        """
        # Create a Product Variant
        product = self.product_obj.create(
            {'name': "Product Product devices",
             'website_published': True}
            )

        # Test No categories
        self.assertEqual(len(product.product_tmpl_id.public_categ_ids), 0)
        # Tes Category has not products
        self.assertFalse(self.category_graphics.has_products_ok)

        product.product_tmpl_id.write(
            {'public_categ_ids': [(6, 0, [self.category_graphics.id])],
             'website_published': True})

        self.assertEqual(len(product.product_tmpl_id.public_categ_ids), 1)
        self.assertTrue(self.category_graphics.has_products_ok)

        # Remove category from product
        product.product_tmpl_id.write(
            {'public_categ_ids': [(3, self.category_graphics.id)]
             })
        # Test No categories
        self.assertEqual(len(product.product_tmpl_id.public_categ_ids), 0)

        # Tes Category has not products
        self.assertFalse(self.category_graphics.has_products_ok)
