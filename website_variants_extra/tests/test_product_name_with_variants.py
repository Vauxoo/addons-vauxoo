# coding: utf-8
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    def test_01_sale_product_name_admin(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_product_name_variants',\
                        'test')",
                        "openerp.Tour.tours.shop_test_product_name_variants",
                        login='admin')

    def test_02_sale_product_name_demo(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_product_name_variants',\
                        'test')",
                        "openerp.Tour.tours.shop_test_product_name_variants",
                        login='demo')

    def test_03_sale_product_name_portal(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_product_name_variants',\
                        'test')",
                        "openerp.Tour.tours.shop_test_product_name_variants",
                        login='portal')

    def test_04_sale_product_name_nouser(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_product_name_variants',\
                        'test')",
                        "openerp.Tour.tours.shop_test_product_name_variants")
