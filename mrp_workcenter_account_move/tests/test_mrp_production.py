# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: hbto@vauxoo.com

from openerp.tests.common import TransactionCase


class TestMrpProduction(TransactionCase):

    """This test do the following:
            1.- Create a mrp.production.
            2.- Proceed to approve.
            3.- Proceed to begin production.
            4.- Proceed with consumption & finish production.
            5.- Check move_id does exist in this test.
            6.- Check move_id.line_id.account_id=rev_production_cost_account,
                credit ==15
            7.- Check move_id.line_id.account_id=
                    rev_inventory_deviation_account,credit ==5
    """

    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        super(TestMrpProduction, self).setUp()
        # Define required global variables.
        self.account_stock_valuation = self.ref('account.stk')
        self.account_wip = self.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.account_cost = self.ref(
            'mrp_workcenter_account_move.rev_production_cost_account')
        self.account_deviation = self.ref(
            'stock_deviation_account.rev_inventory_deviation_account')
        self.mrp_production = self.env['mrp.production'].browse(self.ref(
            'mrp_workcenter_account_move.rev_mrp_production'))
        self.wip_account = self.env.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.wzd_obj = self.env['mrp.product.produce']
        self.wzd_line_obj = self.env['mrp.product.produce.line']

    # Test methods.
    def test_10_approve_begin_consumpt_finish_mrp_production(self):
        # This method approve a mrp production.
        location_obj = self.env['stock.location']
        location_brw = location_obj.search([('name', '=', 'Production')])
        location_brw.write({'valuation_in_account_id': self.wip_account.id,
                            'valuation_out_account_id': self.wip_account.id})
        # Confirm the mrp production.
        self.mrp_production.signal_workflow('button_confirm')
        self.assertEqual(self.mrp_production.state,
                         'confirmed',
                         "The mrp production didn't confirm.")
        # Create the moves needed by mrp production.
        self.mrp_production.action_assign()
        self.assertEqual(self.mrp_production.state,
                         'ready',
                         "The moves aren't ready.")
        # Begin mrp production.
        self.mrp_production.signal_workflow('button_produce')
        self.assertEqual(self.mrp_production.state,
                         'in_production',
                         "The mrp is not in production.")
        # Consumption and finish production.
        self.create_wizard()
        self.assertEqual(self.mrp_production.state,
                         'done',
                         "The mrp production doesn't done.")

        self.production_copy_test(self.mrp_production)

        aml_ids = self.mrp_production.aml_production_ids

        aml_raw_and_fg = [
            u for u in aml_ids
            if u.account_id.id == self.account_stock_valuation]

        # Raw material assertion
        raw_material = sum([x.credit for x in aml_raw_and_fg])
        self.assertEqual(raw_material,
                         85, "Raw Material Consumption is wrong")

        # Finished Good assertion
        finished_goods = sum([y.debit for y in aml_raw_and_fg])
        self.assertEqual(finished_goods,
                         80, "Finished Good Production is wrong")

        # Production Cost assertion
        production_cost = sum([
            v.credit for v in aml_ids
            if v.account_id.id == self.account_cost])
        self.assertEqual(production_cost,
                         15, "Production Cost is wrong")

        # Standard Deviation assertion
        standard_deviation = sum([
            w.debit for w in aml_ids
            if w.account_id.id == self.account_deviation])
        self.assertEqual(standard_deviation,
                         20, "Standard Deviation is wrong")

        # WIP assertion
        wip_ids = [
            o for o in aml_ids
            if o.account_id.id == self.account_wip]

        wip_debit = sum([p.debit for p in wip_ids])
        wip_credit = sum([q.credit for q in wip_ids])
        self.assertEqual((wip_debit, wip_credit),
                         (100, 100), "Work in Process is wrong")

    def production_copy_test(self, production_id=False):
        self.assertTrue(production_id.account_move_id)
        new_production_id = production_id.copy()
        self.assertTrue(new_production_id != production_id)
        self.assertEqual(new_production_id.account_move_id.id, False)

    def create_wizard(self, values=None):
        # Setting Environment
        wz_env = self.wzd_obj.with_context(
            {'active_id': self.mrp_production.id,
             'active_ids': [self.mrp_production.id]})

        # Creating wizard to product
        wz_values = wz_env.default_get([])
        wz_brw = wz_env.create(wz_values)

        # Checking the quantity suggested
        self.assertEqual(wz_brw.product_qty, 1,
                         'The quantity suggested must be 1')

        # Changing the quantity suggested
        wz_brw.product_qty = 1

        values = wz_brw.on_change_qty(wz_brw.product_qty, [])
        values = values.get('value')
        wz_brw.write(values)
        wz_brw.do_produce()
        return True
