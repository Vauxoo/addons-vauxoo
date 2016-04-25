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
    """This test is to know if all the products that were purchased in the
        same order are retrieved to the functional field 'customer_purchased'.
    """

    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.partner_agrolait = self.env.ref('base.res_partner_2')
        self.product_template = self.env.ref(
            'product.product_product_4b_product_template')
        product_list = [
            'product.product_product_4',
            'product.product_product_7',
            'product.product_product_11',
            ]
        self.product_objs = []
        for prod in product_list:
            self.product_objs.append(self.env.ref(prod))

    def test_cap_best_seller_sort(self):
        """This is the test that validates all products that are in the same
        sale order and that they are sorted by the given criteria.
        """
        product_objs = self.product_objs[:]
        for i in range(0, 3):
            if i == 1:
                del product_objs[1]
            sale_order_id = self.sale_order.create(
                {'partner_id': self.partner_agrolait.id, })
            for product in product_objs:
                self.sale_order_line.create(
                    {'order_id': sale_order_id.id,
                     'product_id': product.id,
                     'name': product.name,
                     'product_uom_qty': 2,
                     'price_unit': product.lst_price, })
                expected_sort = [self.product_objs[2].product_tmpl_id.id,
                                 self.product_objs[1].product_tmpl_id.id]
        sort = self.product_template._best_sell_sort(self.product_template)[:2]
        self.assertEqual(sort, expected_sort)
