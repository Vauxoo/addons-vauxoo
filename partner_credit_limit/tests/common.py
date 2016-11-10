# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase
from openerp import tools
from openerp.modules.module import get_module_resource


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.account_invoice_line = self.env['account.invoice.line']

    def _load(self, module, *args):
        tools.convert_file(self.cr, 'account',
                           get_module_resource(module, *args),
                           {}, 'init', False, 'test',
                           self.registry._assertion_report)
