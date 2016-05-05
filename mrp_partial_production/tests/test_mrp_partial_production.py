# coding: utf-8
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger
from openerp.exceptions import Warning as UserError


class TestValidatePickings(TransactionCase):

    def setUp(self):
        super(TestValidatePickings, self).setUp()
        self.mrp = self.env['mrp.production']
        self.wizard = self.env['mrp.product.produce']
        self.w_upd_obj = self.env['stock.change.product.qty']
        self.sale = self.env.ref('mrp_partial_production.sale_order_1')
        self.product = self.env.ref('mrp_partial_production.'
                                    'product_product_18')
        self.compa = self.env.ref('mrp_partial_production.'
                                  'product_product_19')
        self.compb = self.env.ref('mrp_partial_production.'
                                  'product_product_20')
        self.stock = self.env.ref('stock.stock_location_stock')

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_01_produce_partially(self):
        """Test the whole process with partial productions
        """
        mrp_brw = self.mrp.search([('product_id', '=', self.product.id)])

        # Reserving products
        mrp_brw.action_assign()
        # Check the number available to produce
        self.assertEqual(mrp_brw.qty_available_to_produce, 4,
                         'The quantity available to produce must be 4')
        # Checking state
        self.assertEqual(mrp_brw.state, 'ready',
                         'The state of the order must be ready')

        wz_env = self.wizard.\
            with_context({'active_id': mrp_brw.id,
                          'active_ids': [mrp_brw.id]})

        # Creating wizard to product
        wz_values = wz_env.default_get([])
        wz_brw = wz_env.create(wz_values)

        # Checking the quantity suggested
        self.assertEqual(wz_brw.product_qty, 4,
                         'The quantity suggested must be 4')

        # Changing the quantity suggested
        wz_brw.product_qty = 5

        # Raise if the quantity is different to the available to produce
        self.assertRaises(UserError, wz_brw.do_produce)

        wz_brw.product_qty = 4

        picking_brw = self.sale.picking_ids.\
            filtered(lambda a: a.state == 'waiting')

        moves = picking_brw.move_lines.\
            filtered(lambda a: a.state == 'assigned')

        # Checking assigned lines
        self.assertFalse(moves,
                         'The move has an assigned line')

        # Loading Lines
        values = wz_brw.on_change_qty(wz_brw.product_qty, [])
        values = values.get('value')
        wz_brw.write(values)
        wz_brw.do_produce()

        # Check the number available to produce
        self.assertEqual(mrp_brw.qty_available_to_produce, 0,
                         'The quantity available to produce must be 0')

        moves = picking_brw.move_lines.\
            filtered(lambda a: a.state == 'assigned')

        # Checking assigned lines
        self.assertTrue(moves,
                        'The move does not have an assigned line')

        # Checking the quantity assigned
        self.assertEqual(moves.product_uom_qty, 4,
                         'The quantity assigned must be 4')

        # Validating Picking
        picking_brw.do_prepare_partial()

        picking_brw.do_transfer()

        # Check  status.
        self.assertEqual(picking_brw.state, 'done',
                         'Wrong state of outgoing shipment.')

        # Adding new qty available

        self.w_upd_obj.create({
            'product_id': self.compa.id,
            'location_id': self.stock.id,
            'new_quantity': 18,
            }).change_product_qty()

        self.w_upd_obj.create({
            'product_id': self.compb.id,
            'location_id': self.stock.id,
            'new_quantity': 12,
            }).change_product_qty()

        # Reserving products
        mrp_brw.action_assign()
        # Check the number available to produce
        self.assertEqual(mrp_brw.qty_available_to_produce, 6,
                         'The quantity available to produce must be 6')

        # Creating Wizard to produce
        wz_values = wz_env.default_get([])
        wz_brw = wz_env.create(wz_values)

        # Checking the quantity suggested
        self.assertEqual(wz_brw.product_qty, 6,
                         'The quantity suggested must be 6')

        picking_brw = self.sale.picking_ids.\
            filtered(lambda a: a.state == 'waiting')

        moves = picking_brw.move_lines.\
            filtered(lambda a: a.state == 'assigned')

        # Checking assigned lines
        self.assertFalse(moves,
                         'The move has an assigned line')

        # Loading the lines
        values = wz_brw.on_change_qty(wz_brw.product_qty, [])
        values = values.get('value')
        wz_brw.write(values)
        wz_brw.do_produce()

        # Check  status.
        self.assertEqual(mrp_brw.state, 'done',
                         'Wrong state of manufacturing order.')

        moves = picking_brw.move_lines.\
            filtered(lambda a: a.state == 'assigned')

        # Checking assigned lines
        self.assertTrue(moves,
                        'The move does not have an assigned line')

        # Checking the quantity assigned
        self.assertEqual(moves.product_uom_qty, 6,
                         'The quantity assigned must be 6')

        # Validating pickings
        picking_brw.do_prepare_partial()

        picking_brw.do_transfer()

        # Check  status.
        self.assertEqual(picking_brw.state, 'done',
                         'Wrong state of second outgoing shipment.')
