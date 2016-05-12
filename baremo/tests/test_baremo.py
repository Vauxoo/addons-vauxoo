# coding: utf-8
from openerp.tests.common import TransactionCase


class TestBaremo(TransactionCase):

    """Tests for Commissions (commission.payment)
    """

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestBaremo, self).setUp()
        self.company_obj = self.registry('res.company')

    def test_basic_baremo(self):
        cur, uid = self.cr, self.uid
        baremo_id = self.ref('baremo.baremo_book_01')

        company_brw = self.company_obj.browse(cur, uid, 1)
        company_brw.baremo_id = baremo_id
        self.assertEquals(baremo_id, company_brw.baremo_id.id)
        return True
