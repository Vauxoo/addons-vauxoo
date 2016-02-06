# coding: utf-8
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    def test_01_comments_admin(self):
        self.phantom_js("/",
                        "openerp.Tour.run('product_test_comments', 'test')",
                        "openerp.Tour.tours.product_test_comments",
                        login='admin')
