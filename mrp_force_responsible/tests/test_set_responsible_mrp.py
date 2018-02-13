# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: jose@vauxoo.com
#           luis_t@vauxoo.com
from odoo.tests.common import TransactionCase


class TestMrpResponsible(TransactionCase):

    def setUp(self):
        super(TestMrpResponsible, self).setUp()
        self.product = self.env['product.product']
        self.users = self.env['res.users']
        self.mrp = self.env['mrp.production']
        self.procurement_order = self.env['procurement.group']
        self.warehouse_id = self.env.ref('stock.warehouse0')
        self.product_id_mrp = self.env.ref(
            "mrp.product_product_19")
        self.route_manufacture = self.env.ref(
            'mrp.route_warehouse0_manufacture'
        )
        # Creating User
        self.user_id = self.users.create(
            {'name': 'Product Test',
             'login': 'user@test.com'})
        self.product_id_mrp.write(
            {'production_responsible': self.user_id.id})

    def test_create_product(self):
        # Creating MRP
        mrp_id = self.mrp.create(
            {'product_id': self.product_id_mrp.id,
             'product_uom_id': self.product_id_mrp.uom_po_id.id,
             'bom_id': self.env.ref('mrp.mrp_bom_3').id})
        mrp_id.onchange_product_id()
        mrp_brw = self.mrp.browse(mrp_id.id)
        self.assertTrue(mrp_brw.user_id.id == self.user_id.id,
                        'The Responsible was not set correctly')

    def test_responsible_from_procurement_mrp(self):
        'This test validate responsible user is set in '\
            'MO when is created from Procurement'

        self.product_id_mrp.write({
            'route_ids': [(6, 0, [self.route_manufacture.id])],
            'production_responsible': self.user_id.id
        })
        procurement_id = self.procurement_order.create({
            'name': 'Test',
        })
        mrp_num = self.mrp.search(
            [('product_id', '=', self.product_id_mrp.id)])
        procurement_id.run(self.product_id_mrp, 1, self.product_id_mrp.uom_id,
                           self.warehouse_id.lot_stock_id, 'Test', 'Test', {})

        mrp_num_after = self.mrp.search(
            [('product_id', '=', self.product_id_mrp.id)])

        self.assertTrue(len(mrp_num_after) > len(mrp_num),
                        "MO should be created")
        self.assertTrue(
            mrp_num_after[-1].user_id == self.user_id,
            'The Responsible was not set correctly')
