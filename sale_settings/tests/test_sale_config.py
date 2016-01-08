# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded /planned by: Katherine Zaoral <kathy@vauxoo.com>
############################################################################
from openerp.tests import common


class TestSaleConfig(common.TransactionCase):

    def setUp(self):
        super(TestSaleConfig, self).setUp()
        self.config = self.env['sale.config.settings']
        self.company_id = self.env.user.company_id

    def test_01(self):
        """
        Check that the company default is correctly set.
        """
        config = self.config.create({})
        self.assertEqual(config.company_id, self.company_id)
