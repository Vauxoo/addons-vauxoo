# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


from openerp.tests.common import TransactionCase


class TestMessageLog(TransactionCase):
    """
    Search last message and check that must be about Transfer
    """

    def setUp(self):
        super(TestMessageLog, self).setUp()
        self.sale = self.env.ref("stock_picking_log_message"
                                 "_transfer.so_log_message_transfer")

    def test_01(self):
        for picking in self.sale.picking_ids:
            picking = picking.message_ids.search([
                ('body', 'ilike', '%Picking transfered%')])
            self.assertTrue(picking, "The message in log is not correct")
