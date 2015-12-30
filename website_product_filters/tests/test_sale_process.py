# coding: utf-8
import openerp.tests
from openerp.addons.website_sale.tests.test_sale_process import TestUi


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUiNew(TestUi):
    def test_01_admin_shop_tour(self):
        self.phantom_js("/", "openerp.Tour.run('shop', 'test')",
                        "openerp.Tour.tours.shop", login="admin")

    def test_02_admin_checkout(self):
        self.phantom_js("/", "openerp.Tour.run('shop_buy_product', 'test')",
                        "openerp.Tour.tours.shop_buy_product", login="admin")

    def test_03_demo_checkout(self):
        self.phantom_js("/", "openerp.Tour.run('shop_buy_product', 'test')",
                        "openerp.Tour.tours.shop_buy_product", login="demo")

    def test_04_public_checkout(self):
        self.phantom_js("/", "openerp.Tour.run('shop_buy_product', 'test')",
                        "openerp.Tour.tours.shop_buy_product")

openerp.addons.website_sale.tests.test_sale_process = TestUiNew
