# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: oscar@vauxoo.com
#    planned by: Oscar Alcala <oscar@vauxoo.com>
############################################################################

from openerp.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    """
        This test is to know if all the products that were purchased in the
        same order are retrieved to the functional field 'customer_purchased'.
    """

    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.partner_agrolait = self.env.ref('base.res_partner_2')
        self.product_template_id = self.env.ref(
            'product.product_product_4b_product_template')
        self.product_objs = []
        product_list = [
            'product.product_product_4',
            'product.product_product_7',
            'product.product_product_11',
            ]
        self.p1 = self.env.ref('product.product_product_7').product_tmpl_id.id
        self.p2 = self.env.ref('product.product_product_11').product_tmpl_id.id
        for prod in product_list:
            self.product_objs.append(self.env.ref(prod))

    def test_get_purchased(self):
        """
            This is the test that validates all products that are in the same
            sale order.
        """
        sale_order_id = self.sale_order.create(
            {'partner_id': self.partner_agrolait.id, })
        for product in self.product_objs:
            self.sale_order_line.create(
                {'order_id': sale_order_id.id,
                 'product_id': product.id,
                 'name': product.name,
                 'product_uom_qty': 2,
                 'price_unit': product.lst_price, })
        ids = self.product_template_id.customer_purchased
        self.assertEqual(set(ids.ids), set([self.p1, self.p2]))
