# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestPricelistTeam(TransactionCase):

    def setUp(self):
        super(TestPricelistTeam, self).setUp()
        self.test_user = self.env['res.users'].create({
            'name': 'User Test', 'login': 'user_test',
            'password': '123456', 'email': 'user_test@email.com'})
        self.limited_group = self.env.ref(
            'default_warehouse_from_sale_team.'
            'group_limited_default_product_pricelist')
        self.unlimited_group = self.env.ref(
            'default_warehouse_from_sale_team.'
            'group_manager_default_product_pricelist')
        self.sale_team = self.env['crm.case.section'].create({
            'name': 'Test Sale Team', 'alias_contact': 'everyone'})
        self.pricelist_1 = self.env['product.pricelist'].create({
            'name': 'Pricelist Test 1', 'type': 'sale'})
        self.pricelist_2 = self.env['product.pricelist'].create({
            'name': 'Pricelist Test 2', 'type': 'sale'})

    def test_00_limit_pricelist(self):
        """In this test we are probing that the user can only view the
        pricelist that is in your sale team.
        """
        self.sale_team.write({'pricelist_team_ids': [
            (4, self.pricelist_1.id)], 'member_ids': [(4, self.test_user.id)]})
        self.limited_group.write({'users': [(4, self.test_user.id)]})
        self.assertIn(self.test_user, self.limited_group.users)
        pricelists = self.env['product.pricelist'].sudo(
            self.test_user).search([])
        self.assertEqual(self.pricelist_1, pricelists)

    def test_10_all_pricelist(self):
        """In this test we are probing that the user can view all pricelist.
        """
        self.unlimited_group.write({'users': [(4, self.test_user.id)]})
        self.assertNotIn(self.test_user, self.limited_group.users)
        self.assertIn(self.test_user, self.unlimited_group.users)
        pricelists = self.env['product.pricelist'].sudo(
            self.test_user).search([])
        self.assertIn(self.pricelist_1, pricelists)
        self.assertIn(self.pricelist_2, pricelists)
