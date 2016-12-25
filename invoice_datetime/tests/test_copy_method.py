# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from odoo.tests.common import TransactionCase


class TestInvoiceDatetimeCopy(TransactionCase):
    """Test for invoice_datetime copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestInvoiceDatetimeCopy, self).setUp()
        self.invoice_id = self.env.ref('invoice_datetime.invoice_1')

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        self.assertEqual(self.invoice_id.state, 'draft')
        self.invoice_id.action_invoice_open()
        self.assertEqual(self.invoice_id.date,
                         "%s-01-01" % time.strftime('%Y'))
        self.assertEqual(self.invoice_id.date_invoice_tz, False)
        self.assertEqual(self.invoice_id.date_type, False)
        self.assertEqual(self.invoice_id.invoice_datetime, False)

        new_invoice_id = self.invoice_id.copy()
        # When copying an invoice the following values should not be set
        self.assertEqual(new_invoice_id.date_invoice_tz, False)
        self.assertEqual(new_invoice_id.date_type, False)
        self.assertEqual(new_invoice_id.invoice_datetime, False)
