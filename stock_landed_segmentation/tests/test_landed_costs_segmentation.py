# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import Warning as UserError


class TestLandedCostsSegmentation(TransactionCase):

    def setUp(self):
        super(TestLandedCostsSegmentation, self).setUp()
        self.move = self.env['stock.move']
        self.slc = self.env['stock.landed.cost']
        po_01 = self.env.ref('stock_landed_segmentation.po_01')
        po_02 = self.env.ref('stock_landed_segmentation.po_02')
        (po_01 + po_02).button_confirm()
        self.picking_01_id = po_01.picking_ids
        self.picking_02_id = po_02.picking_ids
        self.product_freight_id = self.env.ref(
            'stock_landed_segmentation'
            '.service_standard_periodic_landed_cost_1')
        self.product_insurance_id = self.env.ref(
            'stock_landed_segmentation'
            '.service_standard_periodic_landed_cost_2')
        self.account_insurance_id = self.env.ref(
            'stock_landed_segmentation'
            '.insurance_landed_cost_account')
        self.account_freight_id = self.env.ref(
            'stock_landed_segmentation'
            '.freight_landed_cost_account')

        self.product_01 = self.env.ref(
            'stock_landed_segmentation.product_std_01')

        self.product_02 = self.env.ref(
            'stock_landed_segmentation.product_avg_01')

        self.product_03 = self.env.ref(
            'stock_landed_segmentation.product_real_01')

    def do_picking(self, picking_id=False):
        wizard = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(6, 0, [picking_id.id])]})
        wizard.process()
        self.assertEqual(picking_id.state, 'done')

    def create_landed_cost(self, picking_id,
                           insurance_cost=15000, freight_cost=18000,
                           split_method='by_quantity'):
        return self.slc.create({
            'account_journal_id': self.ref(
                'stock_cost_segmentation.expenses_journal'),
            'picking_ids': [(4, picking_id.id), ],
            'cost_lines': [
                (0, 0, {
                    'name': 'insurance',
                    'product_id': self.product_insurance_id.id,
                    'account_id': self.account_insurance_id.id,
                    'split_method': split_method,
                    'price_unit': insurance_cost,
                    'segmentation_cost': 'subcontracting_cost',
                }),
                (0, 0, {
                    'name': 'freight',
                    'product_id': self.product_freight_id.id,
                    'account_id': self.account_freight_id.id,
                    'split_method': split_method,
                    'price_unit': freight_cost,
                    'segmentation_cost': 'landed_cost',
                }),
            ]
        })

    def create_and_validate_landed_costs(self, picking_id=False,
                                         insurance_cost=15000,
                                         freight_cost=18000):
        slc_id = self.create_landed_cost(picking_id, insurance_cost,
                                         freight_cost)

        self.assertEqual(len(slc_id.picking_ids), 1)
        self.assertEqual(len(slc_id.cost_lines), 2)

        # compute and check landed costs
        slc_id.compute_landed_cost()
        self.assertEqual(len(slc_id.valuation_adjustment_lines), 6)

        # validate landed costs
        slc_id.button_validate()

        return slc_id

    def get_quant(self, picking_id=False, product_id=False):
        move = picking_id.move_lines.filtered(
            lambda a: a.product_id == product_id)
        return move[0] if move else None

    def test_00_user_validations(self):
        self.do_picking(self.picking_01_id)
        landed_cost_id = self.create_landed_cost(self.picking_01_id)
        landed_cost_id.compute_landed_cost()
        landed_cost_id.cost_lines.write({
            'segmentation_cost': False,
        })
        msg_error = 'Please fill the segmentation field in Cost Lines'
        with self.assertRaisesRegexp(UserError, msg_error):
            landed_cost_id.button_validate()

        landed_cost_id = self.create_landed_cost(self.picking_01_id)
        msg_error = 'You cannot validate a landed cost which has no valid.*'
        with self.assertRaisesRegexp(UserError, msg_error):
            landed_cost_id.button_validate()

    def get_out(self, product, qty=1):
        """Generating a sale order to move out the product and update its
        cost(FIFO)"""
        sale = self.env['sale.order'].create(
            {'client_order_ref': 'ref1',
             'name': 'Test_SO001',
             'partner_id': self.env.ref('base.res_partner_4').id,
             'partner_invoice_id':
             self.env.ref('base.res_partner_address_7').id,
             'partner_shipping_id':
             self.env.ref('base.res_partner_address_7').id,
             'picking_policy': 'direct',
             'pricelist_id': self.env.ref('product.list0').id,
             'order_line': [
                 (0, 0,
                  {'product_id': product.id,
                   'price_unit': 50,
                   'name': product.name,
                   'product_uom_qty': qty,
                   'product_uom': self.env.ref('uom.product_uom_unit').id,
                   })]})

        sale.action_confirm()
        self.do_picking(sale.picking_ids)

    def test_01_segmentations(self):
        # check initial product costs
        self.assertEqual(self.product_01.standard_price, 100)
        self.assertEqual(self.product_02.standard_price, 100)
        self.assertEqual(self.product_03.standard_price, 100)

        # make incoming stock movements
        self.do_picking(self.picking_01_id)
        landed_cost_id = self.create_and_validate_landed_costs(
            self.picking_01_id, insurance_cost=15000, freight_cost=18000)
        msg_error = 'Only draft landed costs can be validated'
        with self.assertRaisesRegexp(UserError, msg_error):
            landed_cost_id.button_validate()
        # check inventory valuations
        self.assertEqual(
            sorted(self.picking_01_id.mapped(
                'move_lines.value')),
            [21000, 21000, 21000],
            "Inventory valuations from picking #1 doesn't match")
        self.get_out(self.product_02, 100)
        self.get_out(self.product_03, 100)
        self.get_out(self.product_01, 100)
        self.assertEqual(self.product_02.material_cost, 100)
        self.assertEqual(self.product_02.landed_cost, 120)
        self.assertEqual(self.product_02.production_cost, 0)
        self.assertEqual(self.product_02.subcontracting_cost, 50)
        self.assertEqual(self.product_02.standard_price, 210)

        product_std_quant_id = self.get_quant(self.picking_01_id,
                                              self.product_01)
        product_avg_quant_id = self.get_quant(self.picking_01_id,
                                              self.product_02)
        product_real_quant_id = self.get_quant(self.picking_01_id,
                                               self.product_03)

        # check product costs
        self.assertEqual(self.product_01.standard_price, 210)
        self.assertEqual(self.product_02.standard_price, 210)
        self.assertEqual(self.product_03.standard_price, 210)

        # check quant costs
        self.assertEqual(product_std_quant_id.price_unit, 210)
        self.assertEqual(product_avg_quant_id.price_unit, 210)
        self.assertEqual(product_real_quant_id.price_unit, 210)

        # check segmentation costs (M+L+P+S)
        self.assertEqual(product_std_quant_id.segmentation_cost, 210)
        self.assertEqual(product_avg_quant_id.segmentation_cost, 270)
        self.assertEqual(product_real_quant_id.segmentation_cost, 330)

        self.assertEqual(product_std_quant_id.landed_cost, 60)
        self.assertEqual(product_std_quant_id.material_cost, 100)
        self.assertEqual(product_std_quant_id.subcontracting_cost, 50)

        self.assertEqual(product_avg_quant_id.landed_cost, 120)
        self.assertEqual(product_avg_quant_id.material_cost, 100)
        self.assertEqual(product_avg_quant_id.subcontracting_cost, 50)

        self.assertEqual(product_real_quant_id.landed_cost, 180)
        self.assertEqual(product_real_quant_id.material_cost, 100)
        self.assertEqual(product_real_quant_id.subcontracting_cost, 50)

        # Receive products
        self.do_picking(self.picking_02_id)
        self.create_and_validate_landed_costs(self.picking_02_id,
                                              insurance_cost=31500,
                                              freight_cost=9000)

        # check inventory valuations
        self.assertEqual(
            sorted(self.picking_02_id.mapped(
                'move_lines.value')),
            [28500, 28500, 45000],
            "Inventory valuations from picking #2 doesn't match")

        product_std_quant_id = self.get_quant(self.picking_02_id,
                                              self.product_01)
        product_avg_quant_id = self.get_quant(self.picking_02_id,
                                              self.product_02)
        product_real_quant_id = self.get_quant(self.picking_02_id,
                                               self.product_03)

        # check quant costs
        self.assertEqual(product_std_quant_id.price_unit, 190)
        self.assertEqual(product_avg_quant_id.price_unit, 300)
        self.assertEqual(product_real_quant_id.price_unit, 190)

        # check segmentation costs
        self.assertEqual(product_std_quant_id.segmentation_cost, 190)
        self.assertEqual(product_avg_quant_id.segmentation_cost, 320)
        self.assertEqual(product_real_quant_id.segmentation_cost, 230)

        self.assertEqual(product_std_quant_id.material_cost, 100)
        self.assertEqual(product_avg_quant_id.material_cost, 210)
        self.assertEqual(product_real_quant_id.material_cost, 100)

        self.assertEqual(product_std_quant_id.landed_cost, 20)
        self.assertEqual(product_avg_quant_id.landed_cost, 40)
        self.assertEqual(product_real_quant_id.landed_cost, 60)

        self.assertEqual(product_std_quant_id.subcontracting_cost, 70)
        self.assertEqual(product_avg_quant_id.subcontracting_cost, 70)
        self.assertEqual(product_real_quant_id.subcontracting_cost, 70)

        self.assertEqual(self.product_02.material_cost, 100)
        self.assertEqual(self.product_02.landed_cost, 120)
        self.assertEqual(self.product_02.production_cost, 0)
        self.assertEqual(self.product_02.subcontracting_cost, 50)

        self.get_out(self.product_02, 10)
        self.get_out(self.product_03, 10)
        self.get_out(self.product_01, 10)
        # check product costs
        self.assertEqual(self.product_01.standard_price, 190)
        self.assertEqual(self.product_02.standard_price, 300)
        self.assertEqual(self.product_03.standard_price, 190)

    def get_lines_by_cost_name(self, landed_cost_id, name):
        val_ids = landed_cost_id.valuation_adjustment_lines
        return name and [vid.additional_landed_cost for vid in val_ids
                         if vid.cost_line_id.display_name == name]

    def test_02_split_methods(self):
        vals = [
            'by_quantity',
            'by_weight',
            'by_volume',
            'equal',
            'by_current_cost_price',
        ]

        # leave only the avg one
        move_ids = self.picking_01_id.move_lines
        self.picking_01_id.write({
            'move_lines': [(3, mid.id) for mid in move_ids
                           if mid.product_id != self.product_02]
        })
        for split_method in vals:
            landed_cost_id = self.create_landed_cost(
                picking_id=self.picking_01_id, split_method=split_method)
            landed_cost_id.compute_landed_cost()

            insurance = self.get_lines_by_cost_name(
                landed_cost_id, 'insurance')
            freight = self.get_lines_by_cost_name(landed_cost_id, 'freight')

            self.assertEqual(insurance[0], 15000)
            self.assertEqual(freight[0], 18000)
