# coding: utf-8
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    def test_01_comment_qty_admin(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_test_comment_qty',\
                        'test')",
                        "openerp.Tour.tours.shop_test_comment_qty",
                        login='admin')
