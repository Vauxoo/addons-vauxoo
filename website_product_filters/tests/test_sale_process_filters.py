# coding: utf-8
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    def test_01_sale_process_filters_admin(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_filters', 'test')",
                        "openerp.Tour.tours.shop_test_filters",
                        login='admin')
