# coding: utf-8

from openerp.tests.common import TransactionCase


class TestMrpLocationSrcFromRule(TransactionCase):
    """These tests validate the Locations of MO
        created from procurement
    """

    def setUp(self):
        super(TestMrpLocationSrcFromRule, self).setUp()
        self.product_id = self.env.ref("product.product_product_18")
        self.procurement_rule = self.env['procurement.rule']
        self.procurement_order = self.env['procurement.order']
        self.warehouse_id = self.env.ref('stock.warehouse0')
        self.route_manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture')
        self.location_bom = self.env.ref('stock.stock_location_components')
        self.product_id.write({
            'route_ids': [(6, 0, [self.route_manufacture.id])]})

    def test_mrp_location_src_different(self):
        'This validate when pull rule of manufacture '\
            'has set one location_bom_id different to '\
            'location_id'

        # Search procurement rule of manufacture
        rule_ids = self.procurement_rule.search(
            [('route_id', '=', self.route_manufacture.id),
             ('action', '=', 'manufacture')]
        )
        # Set location_bom_id in procurement rule
        rule_ids.write({'location_bom_id': self.location_bom.id})

        # Create procurement order
        procurement_id = self.procurement_order.create({
            'product_id': self.product_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'name': 'Test',
            'product_qty': 1,
            'product_uom': self.product_id.uom_id.id
        })
        procurement_id.run()
        self.assertTrue(procurement_id.rule_id,
                        "Procurement rule should be set")
        self.assertTrue(procurement_id.production_id, "MO should be created")

        # MO created from Procurement Order should be the location_src_id
        # different to location_dest_id, because was set this location
        # from procurement rule
        self.assertEquals(
            procurement_id.production_id.location_src_id.id,
            self.location_bom.id)
        self.assertEquals(
            procurement_id.production_id.location_dest_id.id,
            self.warehouse_id.lot_stock_id.id)

    def test_mrp_location_same(self):
        'This test validate the normally behavior '\
            'when MO is created from procurement order '\
            'and procurement rule is not set location_bom_id'

        procurement_id = self.procurement_order.create({
            'product_id': self.product_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'name': 'Test',
            'product_qty': 1,
            'product_uom': self.product_id.uom_id.id
        })
        procurement_id.run()
        self.assertTrue(procurement_id.rule_id,
                        "Procurement rule should be set")
        self.assertTrue(procurement_id.production_id, "MO should be created")
        self.assertEquals(
            procurement_id.production_id.location_src_id.id,
            self.warehouse_id.lot_stock_id.id)
        self.assertEquals(
            procurement_id.production_id.location_dest_id.id,
            self.warehouse_id.lot_stock_id.id)
