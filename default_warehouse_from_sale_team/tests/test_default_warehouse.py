# coding: utf-8

from openerp.tests.common import TransactionCase


class TestSalesTeamDefaultWarehouse(TransactionCase):

    def setUp(self):
        super(TestSalesTeamDefaultWarehouse, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_12')
        self.sale_obj = self.registry('sale.order')
        self.purchase_obj = self.registry('purchase.order')
        self.purchase_requisition_obj = self.registry('purchase.requisition')
        self.invoice_obj = self.registry('account.invoice')
        self.res_user_obj = self.env['res.users']
        self.pick_type_obj = self.env['stock.picking.type']

    def test_default_picking_type_purchase_requisition(self):
        """Validate the picking type by default from sale team warehouse in
        purchase requisition"""
        demo_user = self.env.ref('base.user_demo')
        test_wh = self.env.ref('stock.stock_warehouse_shop0')
        sales_team = self.env.ref('sales_team.section_sales_department')

        self.purchase_requisition_obj.create(self.cr, demo_user.id, {})

        demo_user.write({'default_section_id': sales_team.id})
        sales_team.write({'default_warehouse': test_wh.id})

        values = self.purchase_requisition_obj.default_get(
            self.cr, demo_user.id, [])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_id = self.purchase_requisition_obj.create(
            self.cr, demo_user.id, {})
        purchase_brw2 = self.purchase_requisition_obj.browse(
            self.cr, self.uid, purchase_id)

        self.assertEqual(purchase_brw2.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team realted to de user.')

    def test_default_picking_type_purchase(self):
        """Validate picking type by default from sale team warehouse in
        purchase order"""
        demo_user = self.env.ref('base.user_demo')
        location_id = self.env.ref('stock.stock_location_3')
        test_wh = self.env.ref('stock.stock_warehouse_shop0')
        sales_team = self.env.ref('sales_team.section_sales_department')
        purchase_values = {
            'partner_id': self.partner.id,
            'location_id': location_id.id,
            'pricelist_id': self.partner.property_product_pricelist_purchase.id
        }

        self.purchase_obj.create(self.cr, demo_user.id, purchase_values)

        demo_user.write({'default_section_id': sales_team.id})
        sales_team.write({'default_warehouse': test_wh.id})

        values = self.purchase_obj.default_get(self.cr, demo_user.id, [])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_values.update({'name': 'Purchase with sale team'})
        purchase_id = self.purchase_obj.create(
            self.cr, demo_user.id, purchase_values)
        purchase_brw2 = self.purchase_obj.browse(
            self.cr, self.uid, purchase_id)

        self.assertEqual(purchase_brw2.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team realted to de user.')

    def test_proper_behavior(self):
        """1.- Testing that the Demo User has not sales team set.
        2.-Testing that the sales order created by Demo User has
        the main warehouse assigned by default.
        3.- Writing a sales team to Demo user and a default warehouse for
        the sales team related to the Demo User.
        4.- Testing that the sales order created by Demo User after
        the sales team assignation has the default warehouse set
        on the user sales team.
        """
        demo_user = self.env.ref('base.user_demo')
        main_wh = self.env.ref('stock.warehouse0')
        test_wh = self.env.ref('stock.stock_warehouse_shop0')
        sales_team = self.env.ref('sales_team.section_sales_department')
        sale = self.sale_obj.create(self.cr, demo_user.id, {
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'pricelist_id': self.ref('product.list0'),
        })
        sale_brw1 = self.sale_obj.browse(self.cr, self.uid, sale)
        demo_user.write({'default_section_id': sales_team.id})
        sales_team.write({'default_warehouse': test_wh.id})
        sale = self.sale_obj.create(self.cr, demo_user.id, {
            'name': 'Tests Sales Team Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'pricelist_id': self.ref('product.list0'),
        })
        sale_brw2 = self.sale_obj.browse(self.cr, self.uid, sale)
        self.assertEqual(sale_brw1.warehouse_id.id, main_wh.id,
                         'Default warehouse is not the main warehouse.')
        self.assertEqual(sale_brw2.warehouse_id.id, test_wh.id,
                         'Default warehouse is not the warehouse'
                         'set on the sales team realted to de user.')
