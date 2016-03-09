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
            5.- Check segmentation on production products.
    '''

    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        super(TestMrpProduction, self).setUp()
        # Define required global variables.
        self.account_stock_valuation = self.ref('account.stk')
        self.account_cost = self.ref(
            'mrp_workcenter_account_move.rev_production_cost_account')
        self.account_deviation = self.ref(
            'stock_deviation_account.rev_inventory_deviation_account')
        self.mrp_production_d = self.env['mrp.production'].browse(
            self.ref(
                'mrp_workcenter_segmentation.'
                'mrp_production_segmentation_d_product'))
        self.mrp_production_e = self.env['mrp.production'].browse(
            self.ref(
                'mrp_workcenter_segmentation.'
                'mrp_production_segmentation_e_product'))
        self.wip_account = self.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.wzd_obj = self.env['mrp.product.produce']
        self.wzd_line_obj = self.env['mrp.product.produce.line']

    # Test methods.
    def test_10_approve_begin_consumpt_finish_mrp_production(self):
        # This method approve a mrp production.
        quant_obj = self.env['stock.quant']
        location_obj = self.env['stock.location']
        location_brw = location_obj.search([('name', '=', 'Production')])
        location_brw.write({'valuation_in_account_id': self.wip_account,
                            'valuation_out_account_id': self.wip_account})

        # Confirm the mrp production d.
        self.mrp_production_d.signal_workflow('button_confirm')
        self.assertEqual(self.mrp_production_d.state,
                         'confirmed',
                         "The mrp is not in Confirmed state.")

        self.mrp_production_d.action_assign()
        self.assertEqual(self.mrp_production_d.state,
                         'ready',
                         "The mrp is not in Ready state.")

        # Begin mrp production.
        self.mrp_production_d.signal_workflow('button_produce')
        self.assertEqual(self.mrp_production_d.state,
                         'in_production',
                         "The mrp is not in production.")
        # Consumption and finish production.
        self.create_wizard(self.mrp_production_d, qty=1)
        self.create_wizard(self.mrp_production_d, qty=2)
        self.assertEqual(self.mrp_production_d.state,
                         'done',
                         "The mrp production doesn't done.")

        aml_ids = self.mrp_production_d.aml_production_ids

        aml_raw_and_fg = [
            u for u in aml_ids
            if u.account_id.id == self.account_stock_valuation]

        # Raw material assertion
        raw_material = sum([x.credit for x in aml_raw_and_fg])
        self.assertEqual(raw_material,
                         240, "Raw Material Consumption is wrong")

        # Finished Good assertion
        finished_goods = sum([y.debit for y in aml_raw_and_fg])
        self.assertEqual(finished_goods,
                         300, "Finished Good Production is wrong")

        # Production Cost assertion
        production_cost = sum([
            v.credit for v in aml_ids
            if v.account_id.id == self.account_cost])
        self.assertEqual(production_cost,
                         45, "Production Cost is wrong")

        # Standard Deviation assertion
        standard_deviation = sum([
            w.credit for w in aml_ids
            if w.account_id.id == self.account_deviation])
        self.assertEqual(standard_deviation,
                         15, "Standard Deviation is wrong")

        # WIP assertion
        wip_ids = [
            o for o in aml_ids
            if o.account_id.id == self.wip_account]

        wip_debit = sum([p.debit for p in wip_ids])
        wip_credit = sum([q.credit for q in wip_ids])
        self.assertEqual((wip_debit, wip_credit),
                         (300, 300), "Work in Process is wrong")

        quant_brw = quant_obj.search(
            [('product_id', '=', self.mrp_production_d.product_id.id)])
        self.assertEqual(
            sum([qnt.qty for qnt in quant_brw]), 3,
            "Quant quantity in Production is wrong")
        self.assertEqual(quant_brw[0].cost, 100, "Cost on Quant is wrong")
        self.assertEqual(
            quant_brw[0].material_cost, 80,
            "Material Cost on Quant is wrong")
        self.assertEqual(
            quant_brw[0].production_cost, 15,
            "Production Cost on Quant is wrong")

        # Confirm the mrp production e.
        self.mrp_production_e.signal_workflow('button_confirm')
        self.assertEqual(self.mrp_production_e.state,
                         'confirmed',
                         "The mrp is not in Confirmed state.")

        self.mrp_production_e.action_assign()
        self.assertEqual(self.mrp_production_e.state,
                         'ready',
                         "The mrp is not in Ready state.")

        # Begin mrp production.
        self.mrp_production_e.signal_workflow('button_produce')
        self.assertEqual(self.mrp_production_e.state,
                         'in_production',
                         "The mrp is not in production.")

        # Consumption and finish production.
        self.create_wizard(self.mrp_production_e, qty=1)
        self.assertEqual(self.mrp_production_e.state,
                         'done',
                         "The mrp production doesn't done.")

        aml_ids = self.mrp_production_e.aml_production_ids

        aml_raw_and_fg = [
            u for u in aml_ids
            if u.account_id.id == self.account_stock_valuation]

        # Raw material assertion
        raw_material = sum([x.credit for x in aml_raw_and_fg])
        self.assertEqual(raw_material,
                         140, "Raw Material Consumption is wrong")

        # Finished Good assertion
        finished_goods = sum([y.debit for y in aml_raw_and_fg])
        self.assertEqual(finished_goods,
                         150, "Finished Good Production is wrong")

        # Production Cost assertion
        production_cost = sum([
            v.credit for v in aml_ids
            if v.account_id.id == self.account_cost])
        self.assertEqual(production_cost,
                         30, "Production Cost is wrong")

        # Standard Deviation assertion
        standard_deviation = sum([
            w.debit for w in aml_ids
            if w.account_id.id == self.account_deviation])
        self.assertEqual(standard_deviation,
                         20, "Standard Deviation is wrong")

        # WIP assertion
        wip_ids = [
            o for o in aml_ids
            if o.account_id.id == self.wip_account]

        wip_debit = sum([p.debit for p in wip_ids])
        wip_credit = sum([q.credit for q in wip_ids])
        self.assertEqual((wip_debit, wip_credit),
                         (170, 170), "Work in Process is wrong")

        quant_brw = quant_obj.search(
            [('product_id', '=', self.mrp_production_e.product_id.id)])
        self.assertEqual(quant_brw.cost, 150, "Cost on Quant is wrong")
        self.assertEqual(
            quant_brw.material_cost, 120,
            "Material Cost on Quant is wrong")
        self.assertEqual(
            quant_brw.production_cost, 30,
            "Production Cost on Quant is wrong")
        self.assertEqual(
            quant_brw.subcontracting_cost, 15,
            "Subcontracting Cost on Quant is wrong")
        self.assertEqual(
            sum([qnt.qty for qnt in quant_brw]), 1,
            "Production Cost on Quant is wrong")

    def create_wizard(self, mrp_production, qty=1):
        # Setting Environment
        wz_env = self.wzd_obj.with_context(
            {'active_id': mrp_production.id,
             'active_ids': [mrp_production.id]})

        # Creating wizard to product
        wz_values = wz_env.default_get([])
        wz_brw = wz_env.create(wz_values)

        # Changing the quantity suggested
        wz_brw.product_qty = qty

        values = wz_brw.on_change_qty(wz_brw.product_qty, [])
        values = values.get('value')
        wz_brw.write(values)
        wz_brw.do_produce()
        return True
