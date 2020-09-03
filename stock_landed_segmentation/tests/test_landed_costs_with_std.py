from odoo.addons.stock.tests.common import TestStockCommon


class TestLandedCostsWithStd(TestStockCommon):

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestLandedCostsWithStd, self).setUp()
        self.invoice_id = self.env.ref(
            'stock_landed_segmentation.invoice_landing_costs_average_1')

    def create_product(self, values):
        default = dict(
            property_valuation='real_time',
            property_cost_method='fifo',
            weight=10,
            volume=1,
            property_stock_account_input=self.ref(
                'stock_cost_segmentation.o_expense'),
            property_stock_account_output=self.ref(
                'stock_cost_segmentation.o_income'),
        )
        default.update(values)
        return self.ProductObj.create(default)

    def create_standard_product(self, standard_price=1000.0):
        values = dict(
            name='Standard Valuated Product',
            cost_method='fifo',
            standard_price=standard_price,
        )
        self.product_standard = self.create_product(values)

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

    def create_standard_move(self, qty=10):
        self.product_id = self.product_standard
        return self.create_move(qty)

    def confirm_picking(self):
        wizard = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(6, 0, self.picking_id.ids)]})
        wizard.process()

    def create_picking(self):
        self.picking_id = self.PickingObj.create({
            'partner_id': self.partner_delta_id,
            'location_id': self.location_id,
            'location_dest_id': self.location_dest_id,
            'picking_type_id': self.picking_type_id})

    def create_picking_basic(self):
        self.create_standard_product()
        self.picking_type_id = self.picking_type_in
        self.location_id = self.supplier_location
        self.location_dest_id = self.stock_location
        self.create_picking()
        self.create_standard_move()
        self.confirm_picking()

    def change_landing_costs(self, amount):
        self.assertNotEqual(
            len(self.landed_cost_id.cost_lines), 0,
            'Landed Cost should have costs lines!!!')
        value = float(amount) / len(self.landed_cost_id.cost_lines)
        for line in self.landed_cost_id.cost_lines:
            line.write({'price_unit': value})

    def assign_landing_invoice(self):
        self.invoice_id.action_invoice_open()

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

    def create_landed_cost(self):
        self.landed_cost_id = self.env['stock.landed.cost'].create({
            'picking_ids': [(4, self.picking_id.id)],
            'account_journal_id': self.ref(
                'stock_cost_segmentation.expenses_journal'),
        })

    def validate_landed_cost(self):
        self.landed_cost_id.compute_landed_cost()
        self.landed_cost_id.cost_lines.write(
            {'segmentation_cost': 'landed_cost'})
        self.landed_cost_id.button_validate()
        self.assertEquals(
            self.landed_cost_id.state, 'done',
            'Something went wrong. Landed Costs should be Posted!!!')

    def asserting_landing_cost_basic(self):
        self.assertEquals(
            self.product_standard.standard_price, 1000.0,
            'Something went wrong. Standard Product should cost 1000.00!!!')
        move_std = self.env['stock.move'].search(
            [('product_id', '=', self.product_standard.id),
             ('price_unit', '>', 0)])
        self.assertEquals(
            (move_std.value, move_std.price_unit),
            (19173.4, 1917.34),
            'Something went wrong. Average Product value is 10000.00!!!')

    def create_and_validate_landed_cost(self):
        self.create_picking_basic()
        self.create_landed_cost()
        self.assign_landing_invoice()
        self.validate_landed_cost()

    def validate_acct_entries(self, product_id):
        stock_valuation_acct_id = product_id.categ_id.\
            property_stock_valuation_account_id
        acct_move_id = self.landed_cost_id.account_move_id
        for lid in self.landed_cost_id.cost_lines:
            for val in self.landed_cost_id.valuation_adjustment_lines:
                if val.product_id.id != product_id.id or \
                        val.cost_line_id.id != lid.id:
                    continue
                for aml_id in acct_move_id.line_ids:
                    if aml_id.account_id.id == stock_valuation_acct_id.id and \
                            aml_id.product_id.id == product_id.id and \
                            aml_id.name == val.name:
                        amt = aml_id.credit or aml_id.debit
                        self.assertEquals(amt, val.additional_landed_cost)

    def test_01_basic_landed(self):
        self.create_picking_basic()
        self.create_landed_cost()
        self.assign_landing_invoice()
        self.validate_landed_cost()
        self.asserting_landing_cost_basic()

    def test_02_account_entries(self):
        self.create_and_validate_landed_cost()
        self.validate_acct_entries(self.product_standard)
