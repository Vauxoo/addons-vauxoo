# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Hugo Adan <hugo@vauxoo.com>
############################################################################
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    def test_01_shop_comment_bought_admin(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_comment_bought', 'test')",
                        "openerp.Tour.tours.shop_comment_bought",
                        login='admin')

    def test_02_shop_comment_bought_demo(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_comment_bought', 'test')",
                        "openerp.Tour.tours.shop_comment_bought",
                        login='demo')

    def test_03_shop_comment_bought_portal(self):
        self.phantom_js("/",
                        "openerp.Tour.run('shop_comment_bought', 'test')",
                        "openerp.Tour.tours.shop_comment_bought",
                        login='portal')
