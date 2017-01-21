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
import time
from datetime import date
from openerp.tests.common import TransactionCase


class TestCommission(TransactionCase):

    """Tests for Commissions (commission.payment)
    """

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestCommission, self).setUp()
        self.cp_model = self.registry('commission.payment')
        self.php_model = self.registry('product.historic.price')
        self.aml_model = self.registry('account.move.line')
        self.inv_model = self.registry('account.invoice')
        self.prod_model = self.registry('product.product')

    def test_basic_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_1'),
        demo_id = self.ref('base.user_demo'),

        cp_brw = self.cp_model.browse(cur, uid, cp_id)
        cp_brw.action_view_payment()
        cp_brw.action_view_invoice()

        self.assertEquals(
            cp_brw.total_comm, 660,
            'Commission should be 660')

        self.assertEquals(cp_brw.state, 'open',
                          'Commission Should be in State "Open"')

        self.assertEquals(len(cp_brw.salesman_ids) > 0, True,
                          'There should be at least one computation')
        for cs_brw in cp_brw.salesman_ids:
            if not cs_brw.salesman_id:
                continue
            self.assertEquals(cs_brw.salesman_id.id, demo_id[0],
                              'Salesman shall be "Demo User"')
            self.assertEquals(cs_brw.comm_total, 660.00,
                              'Wrong Quantity on commission')

        cp_brw.validate()
        self.assertEquals(
            cp_brw.state, 'done',
            'Commission Should be in State "Done"')

        cp_brw.action_draft()
        self.assertEquals(
            cp_brw.state, 'draft',
            'Commission Should be in State "Draft"')

        return True

    def test_fix_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_1'),
        cp_brw = self.cp_model.browse(cur, uid, cp_id)
        self.assertEquals(
            cp_brw.total_comm, 660,
            'Commission should be 660')
        cp_brw.action_draft()
        self.assertEquals(
            cp_brw.comm_fix, False,
            'There should be no Commission to Fix')
        cp_brw.unknown_salespeople = True
        cp_brw.prepare()
        cp_brw.action_view_fixlines()
        self.assertEquals(
            cp_brw.comm_fix, True,
            'There should be Commissions to Fix')
        self.assertNotEquals(
            cp_brw.total_comm, 660,
            'Commission should not be 660')

        no_salesman = [
            comm
            for comm in cp_brw.comm_line_ids
            if not comm.salesman_id
        ]

        salesman_id = self.ref('base.user_demo')
        for cl_brw in no_salesman:
            cl_brw.salesman_id = salesman_id

        cp_brw.action_recompute()
        self.assertEquals(
            cp_brw.comm_fix, False,
            'There should be no Commission to Fix')

        cp_brw.validate()
        self.assertEquals(
            cp_brw.state, 'done',
            'Commission Should be in State "Done"')

        return True

    def test_aml_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_1')
        cp_brw = self.cp_model.browse(cur, uid, cp_id)
        cp_brw.action_draft()

        month = str((date.today().month % 12) + 1)
        cp_brw.date_start = time.strftime('%Y') + '-' + month + '-01'
        cp_brw.date_stop = time.strftime('%Y') + '-' + month + '-28'
        cp_brw.unknown_salespeople = True

        aml_ids = [self.ref('commission_payment.aml_rec_debit')]
        aml_ids += [self.ref('commission_payment.aml_rec_credit')]
        self.aml_model.reconcile_partial(cur, uid, aml_ids, 'auto')

        cp_brw.prepare()
        self.assertEquals(
            cp_brw.comm_fix, True,
            'There should be Commissions to Fix')
        self.assertEquals(
            cp_brw.total_comm, 0,
            'Commission should be 0')

        no_salesman = [
            comm
            for comm in cp_brw.comm_line_ids
            if not comm.salesman_id
        ]

        salesman_id = self.ref('base.user_demo')
        partner_id = self.ref('base.res_partner_23')
        for cl_brw in no_salesman:
            cl_brw.salesman_id = salesman_id
            cl_brw.partner_id = partner_id

        cp_brw.action_recompute()

        self.assertEquals(
            cp_brw.total_comm, 30,
            'Commission should be 30')

        self.assertEquals(
            cp_brw.comm_fix, False,
            'There should be no Commission to Fix')

        cp_brw.validate()
        self.assertEquals(
            cp_brw.state, 'done',
            'Commission Should be in State "Done"')

        return True

    def test_product_commission(self):
        cur, uid = self.cr, self.uid
        prod_id = self.ref('product.product_product_4')
        prod_brw = self.prod_model.browse(cur, uid, prod_id)

        price_ids = self.php_model.search(
            cur, uid,
            [('product_id', '=', prod_brw.product_tmpl_id.id)])

        self.assertEquals(
            len(price_ids) > 0, True,
            'There should historical prices on product %s' %
            prod_brw.name)

        cp_id = self.ref('commission_payment.commission_1')
        cp_brw = self.cp_model.browse(cur, uid, cp_id)

        cp_brw.action_draft()
        self.assertEquals(
            cp_brw.state, 'draft',
            'Commission Should be in State "Draft"')

        cp_brw.commission_scope = 'product_invoiced'

        cp_brw.prepare()
        self.assertEquals(
            cp_brw.state, 'open',
            'Commission Should be in State "Open"')
        self.assertEquals(
            cp_brw.total_comm, 300,
            'Commission should be 300')

        cp_brw.validate()
        self.assertEquals(
            cp_brw.state, 'done',
            'Commission Should be in State "Done"')

        return True

    def test_partial_payment_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_1'),
        cp_brw = self.cp_model.browse(cur, uid, cp_id)
        cp_brw.action_draft()
        cp_brw.commission_type = 'partial_payment'
        cp_brw.prepare()
        self.assertEquals(
            cp_brw.total_comm, 660,
            'Commission should be 660')
        return True

    def test_matrix_commission(self):
        cur, uid = self.cr, self.uid
        cp_id = self.ref('commission_payment.commission_2')
        cp_brw = self.cp_model.browse(cur, uid, cp_id)

        self.assertEquals(
            cp_brw.state, 'draft',
            'Commission Should be in State "Draft"')

        cp_brw.prepare()
        self.assertEquals(
            cp_brw.state, 'open',
            'Commission Should be in State "Open"')
        self.assertEquals(
            cp_brw.salesman_ids[0].comm_voucher_ids[0].commission, 500,
            'Commission should be 500')

        self.assertEquals(
            cp_brw.total_comm, 500,
            'Commission should be 500')

        return True
