# coding: utf-8
from openerp.tests.common import TransactionCase
import time


class TestHistoricalPrice(TransactionCase):

    def setUp(self):
        super(TestHistoricalPrice, self).setUp()
        self.product = self.registry('product.template')
        self.h_price = self.registry('product.historic.price')
        self.h_cost = self.registry('product.price.history')
        self.product_id = None

    def test_create_product(self):
        cr, uid = self.cr, self.uid
        # Creating a product
        self.product_id = self.product.create(cr, uid,
                                              {'name': 'Product Test',
                                               'list_price': 25,
                                               'standard_price': 15})
        # Checking if the historical was created correctly
        h_price = self.h_price.search(cr, uid,
                                      [('product_id', '=', self.product_id)])
        h_cost = self.h_cost.search(cr, uid,
                                    [('product_template_id', '=',
                                      self.product_id)])
        self.assertTrue(h_price and h_cost,
                        "The historical were not created correctly")
        price = h_price and self.h_price.browse(cr, uid, h_price[0]).price
        cost = h_cost and self.h_cost.browse(cr, uid, h_cost[0]).cost
        self.assertTrue(price == 25,
                        "The sale price was to saved correctly")
        self.assertTrue(cost == 15,
                        "The cost was to saved correctly")

    def test_write_product(self):
        cr, uid = self.cr, self.uid
        # Updating the product
        self.test_create_product()
        time.sleep(2)
        self.product.write(cr, uid, [self.product_id],
                           {'list_price': 40, 'standard_price': 18})
        # Checking if the historical was changed correctly
        h_price = self.h_price.search(cr, uid,
                                      [('product_id', '=', self.product_id)],
                                      order='name desc', limit=1)
        h_cost = self.h_cost.search(cr, uid,
                                    [('product_template_id', '=',
                                      self.product_id)],
                                    order='datetime desc', limit=1)
        self.assertTrue(h_price and h_cost,
                        "The historical does not exist")
        price = h_price and self.h_price.browse(cr, uid, h_price[0]).price
        cost = h_cost and self.h_cost.browse(cr, uid, h_cost[0]).cost
        self.assertTrue(price == 40,
                        "The sale price was not changed correctly")
        self.assertTrue(cost == 18,
                        "The cost was not changed correctly")
