# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: hbto@vauxoo.com

from collections import namedtuple
from odoo.tests.common import TransactionCase


class TestWorkcenterSegmentation(TransactionCase):

    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        super(TestWorkcenterSegmentation, self).setUp()
        # Define required global variables.
        self.slc = self.env['stock.landed.cost']
        self.slc_id = self.env.ref('mrp_workcenter_segmentation.slc_01')
        self.account_cost = self.ref(
            'mrp_workcenter_account_move.rev_production_cost_account')
        self.account_deviation = self.ref(
            'stock_deviation_account.rev_inventory_deviation_account')
        self.mrp_production_d = self.env.ref(
            'mrp_workcenter_segmentation.'
            'mrp_production_segmentation_d_product')
        self.mrp_production_e = self.env.ref(
            'mrp_workcenter_segmentation.'
            'mrp_production_segmentation_e_product')
        self.wip_account = self.env.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.wizard = self.env['mrp.product.produce']
        self.wizard_line = self.env['mrp.product.produce.line']
        self.location = self.env['stock.location']
        location_id = self.location.search([('name', '=', 'Production')])
        location_id.write({
            'valuation_in_account_id': self.wip_account.id,
            'valuation_out_account_id': self.wip_account.id
        })
        self.summary = namedtuple('summary', ['debit', 'credit', 'name'])

    def produce_product(self, production_id, qty=1, hour=1):
        # Confirm the mrp production d.
        production_id.action_assign()
        self.assertEqual(production_id.state, 'confirmed')
        production_id.button_plan()
        self.assertEqual(production_id.state, 'planned')
        wo_ids = production_id.workorder_ids
        for wo in wo_ids:
            wo.write({'duration': 60 * hour})

        wizard_id = self.env['mrp.product.produce'].with_context(
            {'active_id': production_id.id,
             'active_ids': [production_id.id]}).create(
                 {'product_qty': qty})
        wizard_id.do_produce()
        production_id.button_mark_done()
        self.assertEqual(production_id.state, 'done')

    def get_account_values(self, production_id, account_name):
        rec_ids = production_id.account_move_id.line_ids.filtered(
            lambda l: l.account_id.name == account_name)
        debit, credit = 0, 0
        for rec_id in rec_ids:
            debit += rec_id.debit
            credit += rec_id.credit
        res = self.summary(debit, credit, account_name)
        return res

    def test_01_check_workcenters_segments(self):
        self.slc_id.compute_landed_cost()
        self.slc_id.button_validate()
        self.assertTrue(self.slc_id.state != 'draft')
        self.produce_product(self.mrp_production_d, 3)
        segments_costs = self.mrp_production_d.\
            get_workcenter_segmentation_amount()
        self.assertEqual(segments_costs['material_cost'], 0)
        self.assertEqual(segments_costs['landed_cost'], 0)
        self.assertEqual(segments_costs['production_cost'], 15)
        self.assertEqual(segments_costs['subcontracting_cost'], 0)

        self.produce_product(self.mrp_production_e, 1)

        production_vals = self.get_account_values(self.mrp_production_e,
                                                  'PRODUCTION_COST_ACCOUNT')
        self.assertEqual(production_vals.debit, 0)
        self.assertEqual(production_vals.credit, 22.5)

        deviation_vals = self.get_account_values(self.mrp_production_e,
                                                 'INVENTORY_DEVIATION_ACCOUNT')
        self.assertEqual(deviation_vals.debit, 12.5)
        self.assertEqual(deviation_vals.credit, 0)

        wip_vals = self.get_account_values(self.mrp_production_e,
                                           'WORK_IN_PROCESS')
        self.assertEqual(wip_vals.debit, 22.5)
        self.assertEqual(wip_vals.credit, 12.5)

        segments_costs = self.mrp_production_e.\
            get_workcenter_segmentation_amount()
        self.assertEqual(segments_costs['material_cost'], 0)
        self.assertEqual(segments_costs['landed_cost'], 0)
        self.assertEqual(segments_costs['production_cost'], 15)
        self.assertEqual(segments_costs['subcontracting_cost'], 7.5)
