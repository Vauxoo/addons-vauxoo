# coding: utf-8
import openerp.tests
from openerp.addons.website_sale_options.tests.test_customize import TestUi


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUiNew(TestUi):
    def test_01_admin_shop_tour(self):
        self.phantom_js("/", "openerp.Tour.run('shop_customize', 'test')",
                        "openerp.Tour.tours.shop_customize", login="admin")

openerp.addons.website_sale_options.tests.test_customize.TestUi = TestUiNew
