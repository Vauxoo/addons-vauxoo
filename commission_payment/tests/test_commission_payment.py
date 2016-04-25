# coding: utf-8

"""Definition of the module testing cases (unittest)
"""

###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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


class TestCommission(TransactionCase):

    """Tests for Commissions (commission.payment)
    """

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestCommission, self).setUp()
        self.cp_model = self.registry('commission.payment')

    def test_basic_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_1'),
        demo_id = self.ref('base.user_demo'),

        cp_brw = self.cp_model.browse(cur, uid, cp_id)
        self.assertEquals(cp_brw.state, 'open')

        self.assertEquals(len(cp_brw.salesman_ids) > 0, True,
                          'There should be at least one computation')
        for cs_brw in cp_brw.salesman_ids:
            if not cs_brw.salesman_id:
                continue
            self.assertEquals(cs_brw.salesman_id.id, demo_id[0],
                              'Salesman shall be "Demo User"')
            self.assertEquals(cs_brw.comm_total, 660.00,
                              'Wrong Quantity on commission')

        return True
