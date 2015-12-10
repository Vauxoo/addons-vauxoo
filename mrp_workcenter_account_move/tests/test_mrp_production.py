# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: hbto@vauxoo.com

from openerp.tests.common import TransactionCase


class TestMrpProduction(TransactionCase):
    '''
        This test do the following:
            1.- Create a mrp.production.
            2.- Proceed to approve.
            3.- Proceed to begin production.
            4.- Proceed with consumption & finish production.
            5.- Check move_id does exist in this test.
            6.- Check move_id.line_id.account_id=rev_production_cost_account,
                credit ==15
            7.- Check move_id.line_id.account_id=rev_inventory_deviation_account,
                credit ==5
    '''
    def setUp(self):
        # Pseudo-constructor method of the setUp test.
        super(TestMrpProduction, self).setUp()
        # Define required global variables.
        self.mrp_production = self.env['mrp.production'].browse(self.ref(
             'mrp_workcenter_account_move.rev_mrp_production'))

    def test_10_approve_mrp_production(self):
        # This method approve a mrp production.
        mrp_product = self.mrp_production
