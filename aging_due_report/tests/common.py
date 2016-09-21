# coding: utf-8
# ##########################################################################
#    Module Writen to ODOO, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
# ###########################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
# ###########################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

import logging
from openerp.tests import common
_logger = logging.getLogger(__name__)


class TestAgingCommon(common.TransactionCase):

    def setUp(self):
        super(TestAgingCommon, self).setUp()

        self.invoice_obj = self.env['account.invoice']
        self.partner_obj = self.env['res.partner']
        self.wiz_aging_obj = self.env['account.aging.wizard']
        self.attachment_obj = self.env['ir.attachment']

        self.invoice_demo = self.env.ref('account.test_invoice_1')

        self.partner_id = self.partner_obj.create({'name': 'Partner'})
