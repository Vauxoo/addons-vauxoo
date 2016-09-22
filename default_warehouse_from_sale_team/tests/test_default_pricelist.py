# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestDefaultPricelist(TransactionCase):

    def setUp(self):
        super(TestDefaultPricelist, self).setUp()
        self.test_user = self.env['res.users'].create({
            'name': 'User Test', 'login': 'user_test',
            'password': '123456', 'email': 'user_test@email.com',
            'sel_groups_9_45_10': 9, 'sel_groups_61_62': 61,
            'sel_groups_59_60': 59, 'sel_groups_50_51': 51,
            'sel_groups_46_47': 47})
        self.limited_group = self.env.ref(
            'default_warehouse_from_sale_team.'
            'group_limited_default_product_pricelist')
        self.limited_group.write({'users': [(4, self.test_user.id)]})
        self.warehouse = self.env.ref('stock.warehouse0')
        self.sale_team = self.env['crm.case.section'].create({
            'name': 'Test Sale Team',
            'alias_contact': 'everyone',
            'default_warehouse': self.warehouse.id,
            'member_ids': [(4, self.test_user.id)], })
        self.pricelist_def_sale = self.env['product.pricelist'].create({
            'name': 'Pricelist Default Sale', 'type': 'sale'})
        self.pricelist_def_purchase = self.env['product.pricelist'].create({
            'name': 'Pricelist Default Purchase', 'type': 'purchase'})
        self.pricelist_sale = self.env['product.pricelist'].create({
            'name': 'Pricelist Test Sale', 'type': 'sale'})
        self.pricelist_purchase = self.env['product.pricelist'].create({
            'name': 'Pricelist Test Purchase', 'type': 'purchase'})
        self.partner_sale = self.env.ref('base.res_partner_9')
        self.partner_purchase = self.env.ref('base.res_partner_4')
        self.dict_vals_sale = {
            'partner_id': self.partner_sale.id,
            'partner_invoice_id': self.partner_sale.id,
            'partner_shipping_id': self.partner_sale.id,
            'warehouse_id': self.warehouse.id,
        }

    def test_00_sale_without_pricelist(self):
        """In this test we are probing a sale team without default sale
        pricelist or pricelist's available.
        """
        self.assertIn(self.test_user, self.limited_group.users)

        # The sale_order must be created with partner pricelist
        sale_order = self.env['sale.order'].sudo(
            self.test_user).create(self.dict_vals_sale)
        self.assertEqual(sale_order.pricelist_id,
                         self.partner_sale.property_product_pricelist)

    def test_10_sale_without_pricelist_default(self):
        """In this test we are probing that sale order is created with first
        pricelist in pricelist's available in user sale team.
        """
        self.sale_team.write({
            'pricelist_team_ids': [(6, 0, [self.pricelist_sale.id,
                                           self.pricelist_purchase.id]), ]})

        sale_order = self.env['sale.order'].sudo(
            self.test_user).create(self.dict_vals_sale)

        sale_order.get_pricelist_from_partner_id()
        self.assertEqual(sale_order.pricelist_id, self.pricelist_sale)

        sale_order.get_pricelist_from_warehouse_id()
        self.assertEqual(sale_order.pricelist_id, self.pricelist_sale)

    def test_20_sale_with_pricelist_default(self):
        """In this test we are probing that sale order is created with
        default sale pricelist.
        """
        self.sale_team.write({
            'pricelist_team_ids': [(6, 0, [
                self.pricelist_def_sale.id, self.pricelist_sale.id,
                self.pricelist_purchase.id]), ],
            'default_sale_pricelist': self.pricelist_def_sale.id})

        sale_order = self.env['sale.order'].sudo(
            self.test_user).create(self.dict_vals_sale)

        sale_order.get_pricelist_from_partner_id()
        self.assertEqual(sale_order.pricelist_id, self.pricelist_def_sale)

        sale_order.get_pricelist_from_warehouse_id()
        self.assertEqual(sale_order.pricelist_id, self.pricelist_def_sale)

    def test_30_purchase_with_pricelist_default(self):
        """In this test we are probing that purchase order is created with
        default purchase pricelist.
        """
        self.sale_team.write({
            'pricelist_team_ids': [(6, 0, [
                self.pricelist_sale.id, self.pricelist_def_purchase.id,
                self.pricelist_purchase.id]), ],
            'default_purchase_pricelist': self.pricelist_def_purchase.id})
        dict_vals = {
            'partner_id': self.partner_purchase.id,
            'pricelist_id': self.ref('product.list0'),
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
        }

        purchase_order = self.env['purchase.order'].sudo(
            self.test_user).create(dict_vals)

        purchase_order.get_pricelist_from_partner_id()
        self.assertEqual(purchase_order.pricelist_id,
                         self.pricelist_def_purchase)

        purchase_order.get_pricelist_from_picking_type_id()
        self.assertEqual(purchase_order.pricelist_id,
                         self.pricelist_def_purchase)
