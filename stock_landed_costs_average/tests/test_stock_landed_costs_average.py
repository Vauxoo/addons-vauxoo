# -*- coding: utf-8 -*-

from openerp.addons.stock.tests.common import TestStockCommon


class TestsLandedCosts(TestStockCommon):

    """
    Testint Stock Landed Costs for Average Case
    1. Create a product
    2. Provide inventory prior to reception of material by importation
    2.a.- Can I provide valuation when creating inventory
    3. Provide new picking from importation.
    4. Provide a Product of type landed cost.
    4.1. Provide Invoice with landed costs item to be used in landed cost doc.
    5. Create a Landed Costs Document
    6. compute landed costs.
    7. approve landed Costs.
    """

    def setUp(self):
        """
        basic method to define some basic data to be re use in all test cases.
        """
        super(TestsLandedCosts, self).setUp()
        self.quant = self.env['stock.quant']
        self.invoice_obj = self.env['account.invoice']
        self.return_obj = self.env['stock.return.picking']
        self.picking_type_internal = self.ModelDataObj.xmlid_to_res_id(
            'stock.picking_type_internal')
        self.invoice_id = self.ref(
            'stock_landed_costs_average.invoice_landing_costs_average_1')
        self.invoice_id = self.invoice_obj.browse(self.invoice_id)

    def create_product(self, values):
        default = dict(
            valuation='real_time',
            weight=10,
            volume=1,
            property_stock_account_input=self.ref('account.o_expense'),
            property_stock_account_output=self.ref('account.o_income'),
        )
        default.update(values)
        return self.ProductObj.create(default)

    def create_real_product(self):
        values = dict(
            name='Real Valuated Product',
            cost_method='real',
        )
        self.product_real = self.create_product(values)
        return True

    def create_average_product(self, standard_price=1000.0):
        values = dict(
            name='Average Valuated Product',
            cost_method='average',
            standard_price=standard_price,
        )
        self.product_average = self.create_product(values)
        return True

    def create_move(self, qty, price_unit=0.0):
        default = {
            'name': self.product_id.name,
            'product_uom_qty': qty,
            'price_unit': price_unit,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'picking_id': self.picking_id.id,
            'location_id': self.location_id,
            'location_dest_id': self.location_dest_id
        }
        return self.MoveObj.create(default)

    def create_average_move(self, qty=10, price=0.0):
        self.product_id = self.product_average
        return self.create_move(qty, price)

    def create_real_move(self, qty=10):
        self.product_id = self.product_real
        return self.create_move(qty)

    def confirm_picking(self):
        self.picking_id.action_confirm()
        self.picking_id.action_assign()
        self.assertEquals(
            self.picking_id.state, 'assigned',
            'Something went wrong. Picking should be Ready to Transfer!!!')
        self.picking_id.do_transfer()
        self.assertEquals(
            self.picking_id.state, 'done',
            'Something went wrong. Picking should be Done!!!')
        return True

    def create_picking(self):
        self.picking_id = self.PickingObj.create({
            'partner_id': self.partner_delta_id,
            'picking_type_id': self.picking_type_id})
        return True

    def create_picking_basic(self):
        self.create_average_product()
        self.create_real_product()
        self.picking_type_id = self.picking_type_in
        self.create_picking()
        self.location_id = self.supplier_location
        self.location_dest_id = self.stock_location
        self.create_average_move()
        self.create_real_move()
        self.confirm_picking()
        return True

    def change_landing_costs(self, amount):
        self.assertNotEqual(
            len(self.landed_cost_id.cost_lines), 0,
            'Landed Cost should have costs lines!!!')
        value = float(amount) / len(self.landed_cost_id.cost_lines)
        for line in self.landed_cost_id.cost_lines:
            line.write({'price_unit': value})
        return True

    def assign_landing_invoice(self):
        self.invoice_id.signal_workflow('invoice_open')

        self.assertEquals(
            self.invoice_id.state, 'open',
            'Something went wrong. Invoice should be open!!!')

        wizard_obj = self.env['attach.invoice.to.landed.costs.wizard']
        wizard_brw = wizard_obj.with_context(
            {'active_id': self.invoice_id.id}).create(
                {'stock_landed_cost_id': self.landed_cost_id.id})
        wizard_brw.add_landed_costs()
        self.assertEquals(
            bool(self.invoice_id.stock_landed_cost_id.id), True,
            'Invoice should be attached to a Landed Cost!!!')
        self.landed_cost_id.get_costs_from_invoices()
        return True

    def revert_landed_cost(self):
        landed_cost_id = self.landed_cost_id
        self.landed_cost_id = landed_cost_id.copy()
        self.landed_cost_id.write({
            'picking_ids': [(4, self.picking_id.id)],
        })

        for line in self.landed_cost_id.cost_lines:
            line.write({'price_unit': -1 * line.price_unit})
        self.validate_landed_cost()
        self.reverted_landed_cost = self.landed_cost_id
        self.landed_cost_id = landed_cost_id
        return True

    def create_landed_cost(self):
        self.landed_cost_id = self.env['stock.landed.cost'].create({
            'picking_ids': [(4, self.picking_id.id)],
            'account_journal_id': self.ref('account.expenses_journal'),
        })
        return True

    def validate_landed_cost(self):
        self.landed_cost_id.compute_landed_cost()
        self.landed_cost_id.button_validate()
        self.assertEquals(
            self.landed_cost_id.state, 'done',
            'Something went wrong. Landed Costs should be Posted!!!')
        return True

    def asserting_landing_cost_basic(self):
        self.assertEquals(
            self.product_average.standard_price, 1300.0,
            'Something went wrong. Average Product should cost 1300.00!!!')
        self.assertEquals(
            self.product_real.standard_price, 0.0,
            'Something went wrong. Real Product should cost 0.00!!!')
        quant_real = self.quant.search(
            [('product_id', '=', self.product_real.id)])
        quant_average = self.quant.search(
            [('product_id', '=', self.product_average.id)])

        self.assertEquals(
            (quant_average.inventory_value, quant_average.cost),
            (13000.0, 1300.0),
            'Something went wrong. Average Product value is 3000.00!!!')

        self.assertEquals(
            (quant_real.inventory_value, quant_real.cost),
            (3000.0, 300.0),
            'Something went wrong. Real Product value is 3000.00!!!')

        return True

    def test_basic_landed(self):
        self.create_picking_basic()
        self.create_landed_cost()
        self.assign_landing_invoice()
        self.validate_landed_cost()
        self.asserting_landing_cost_basic()
        self.revert_landed_cost()

        return True

    def create_picking_avg_importation(self, qty, price):
        self.picking_type_id = self.picking_type_in
        self.create_picking()
        self.location_id = self.supplier_location
        self.location_dest_id = self.stock_location
        self.create_average_move(qty, price)
        self.confirm_picking()
        return True

    def return_picking_maquila(self):
        ctx = dict(active_id=self.picking_id.id)
        values = self.return_obj._model.default_get(
            self.cr, self.uid, ['product_return_moves'], context=ctx)

        return_id = self.return_obj.create(dict(invoice_state='none'))

        for val in values['product_return_moves']:
            val['wizard_id'] = return_id.id
            return_id.product_return_moves.create(val)

        new_picking_id = self.return_obj._model._create_returns(
            self.cr, self.uid, [return_id.id], context=ctx)[0]

        self.picking_id = self.PickingObj.browse(new_picking_id)
        self.confirm_picking()
        return True

    def create_picking_maquila(self, qty):
        self.picking_type_id = self.picking_type_internal
        self.create_picking()
        self.location_id = self.stock_location
        self.location_dest_id = self.stock_location
        self.move_maquila = self.create_average_move(qty)
        self.confirm_picking()
        return True

    def assert_average_product_avg(self, avg):
        self.assertEquals(
            self.product_average.standard_price, avg,
            'Something went wrong. Standard Price should be %s!!!' % avg)
        return True

    def assert_average_product_cost(self, cost):
        for quant in self.picking_id.move_lines.quant_ids:
            self.assertEquals(
                quant.cost, cost,
                'Something went wrong. Quant Cost should be %s!!!' % cost)

        return True

    def test_contractor_landed_cost(self):
        # Creating Average Product
        self.create_average_product()

        # Creating Importation of Average Product
        self.create_picking_avg_importation(10, 100)

        self.assert_average_product_avg(100.0)
        self.assert_average_product_cost(100.0)

        # Apply Landed Costs to importation
        self.create_landed_cost()
        self.assign_landing_invoice()
        self.change_landing_costs(500.0)
        self.validate_landed_cost()

        self.assert_average_product_avg(150.0)
        self.assert_average_product_cost(150.0)

        # Send part of importation to Maquila
        self.create_picking_maquila(5)
        picking_maquila_id = self.picking_id

        self.assert_average_product_avg(150.0)
        self.assert_average_product_cost(150.0)

        # Buy new products (Another importation)
        self.create_picking_avg_importation(10, 120)
        self.assert_average_product_avg(135.0)
        self.assert_average_product_cost(120.0)
        # No landed costs have been applies because that is no longer the case

        # Return Produts from Maquila
        self.picking_id = picking_maquila_id
        self.return_picking_maquila()
        self.assert_average_product_avg(135.0)
        self.assert_average_product_cost(150.0)

        # Apply Landed Costs to Maquila
        self.create_landed_cost()
        self.invoice_id = self.invoice_id.copy()
        self.assign_landing_invoice()
        self.change_landing_costs(800.0)
        self.validate_landed_cost()
        self.assert_average_product_avg(175.0)
        self.assert_average_product_cost(310.0)

        return True
