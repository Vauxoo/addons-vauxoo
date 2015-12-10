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
            7.- Check move_id.line_id.account_id=
                    rev_inventory_deviation_account,credit ==5
    '''


    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        super(TestMrpProduction, self).setUp()
        # Define required global variables.
        self.mrp_production = self.env['mrp.production'].browse(self.ref(
             'mrp_workcenter_account_move.rev_mrp_production'))

    # Test methods.
    def test_10_approve_begin_consumpt_finish_mrp_production(self):
        # This method approve a mrp production.
        mrp_product = self.mrp_production
        # Confirm the mrp production.
        mrp_product.signal_workflow('button_confirm')
        self.assertEqual(mrp_product.state,
                         'confirmed',
                         "The mrp production doesn't confirmed.")
        # Create the moves needed by mrp production.
        mrp_product.signal_workflow('moves_ready')
        self.assertEqual(mrp_product.state,
                         'ready',
                         "The moves aren't ready.")
        # Begin mrp production.
        mrp_product.signal_workflow('button_produce')
        self.assertEqual(mrp_product.state,
                         'in_production',
                         "The mrp is not in production.")
        # Consumption and finish production.
        mrp_product.signal_workflow('button_produce_done')
        self.assertEqual(mrp_product.state,
                         'done',
                         "The mrp production doesn't done.")
