# coding: utf-8
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from openerp.tests.common import TransactionCase


class TestSaleWebsiteCleanup(TransactionCase):
    """In order to test the cancellation of draft orders that have been
    created by the public user over 24 hours ago.
    So, this test does the following:

    1. Update a draft order setting a past date and the public user as partner.
    2. Call the cancel_old_orders method to cancel the previous draft order.
    3. Do an assertTrue to verify that the cancellation was successful.
    """

    def setUp(self):
        """Define global variables to test method."""
        super(TestSaleWebsiteCleanup, self).setUp()
        self.sale_order_obj = self.env['sale.order']
        self.order = self.env.ref('sale.sale_order_8')
        self.partner = self.env.ref('base.public_user')

    def test_10_cancel_draft_orders(self):
        """Cancel draft orders that were created by the public user
        over 24 hours ago.
        """
        self.order.write({
            'partner_id': self.partner.id,
            'date_order': '2015-05-08 18:17:05',
        })
        self.sale_order_obj.cancel_old_orders()
        self.assertTrue(self.order.state == 'cancel',
                        'The order was not cancelled.')
