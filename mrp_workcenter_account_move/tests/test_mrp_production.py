# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: hbto@vauxoo.com

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProduction(TestMrpCommon):

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
        self.account_stock_valuation = self.env['account.account'].search([
            ('code', '=', '100111')])
        self.account_cost = self.env.ref(
            'mrp_workcenter_account_move.rev_production_cost_account')
        self.account_deviation = self.env.ref(
            'stock_deviation_account.rev_inventory_deviation_account')
        self.mrp_production = self.env.ref(
            'mrp_workcenter_account_move.rev_mrp_production')
        self.wip_account = self.env.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.env.ref('mrp_workcenter_account_move.rev_routing').write(
            {'journal_id': self.env.ref(
                'mrp_routing_account_journal.landed_cost_journal_1').id})
        self.env.ref('base.main_company').write({
            'gain_inventory_deviation_account_id': self.account_deviation.id,
            'loss_inventory_deviation_account_id': self.account_deviation.id, 
        })

    # Test methods.
    def test_10_approve_begin_consumpt_finish_mrp_production(self):
        # This method approve a mrp production.
        location_obj = self.env['stock.location']
        location_brw = location_obj.search([('name', '=', 'Production')])
        location_brw.write({'valuation_in_account_id': self.wip_account.id,
                            'valuation_out_account_id': self.wip_account.id})
        self.assertEqual(self.mrp_production.state,
                         'confirmed',
                         "The mrp production didn't confirm.")
        # Create the moves needed by mrp production.
        self.mrp_production.action_assign()
        self.mrp_production.button_plan()
        # Consumption and finish production.
        self.create_wizard(self.mrp_production)
        self.assertEqual(self.mrp_production.state,
                         'done',
                         "The mrp production isn't done.")

        self.production_copy_test(self.mrp_production)

        aml_ids = self.mrp_production.aml_production_ids

        aml_raw_and_fg = [
            u for u in aml_ids
            if u.account_id == self.account_stock_valuation]

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
            if v.account_id == self.account_cost])
        self.assertEqual(production_cost,
                         15, "Production Cost is wrong")

        # Standard Deviation assertion
        standard_deviation = sum([
            w.debit for w in aml_ids
            if w.account_id == self.account_deviation])
        self.assertEqual(standard_deviation,
                         20, "Standard Deviation is wrong")

        # WIP assertion
        wip_ids = [
            o for o in aml_ids
            if o.account_id == self.wip_account]

        wip_debit = sum([p.debit for p in wip_ids])
        wip_credit = sum([q.credit for q in wip_ids])
        self.assertEqual((wip_debit, wip_credit),
                         (100, 100), "Work in Process is wrong")

    def production_copy_test(self, production_id=False):
        self.assertTrue(production_id.account_move_id)
        new_production_id = production_id.copy()
        self.assertTrue(new_production_id != production_id)
        self.assertEqual(new_production_id.account_move_id.id, False)

    def create_wizard(self, production_id=False):
        wo_ids = production_id.workorder_ids
        for wo in wo_ids:
            wo.write({'duration': 60})

        self.wizard_id = self.env['mrp.product.produce'].sudo(
            self.user_mrp_user).with_context({
                'active_id': production_id.id,
                'active_ids': [production_id.id],
        }).create({
            'product_qty': 1.0,
        })
        self.wizard_id.do_produce()
        production_id.button_mark_done()

    def produce(self, production_id=False):
        wo_ids = production_id.workorder_ids
        for wo in wo_ids:
            wo.button_start()
            wo.record_production()
            wo.write({'duration': 60})
        production_id.button_mark_done()
