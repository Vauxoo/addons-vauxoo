# coding: utf-8

from openerp.tests.common import TransactionCase


class TestSalesTeamDefaultWarehouse(TransactionCase):

    def setUp(self):
        super(TestSalesTeamDefaultWarehouse, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_12')
        self.sale_obj = self.registry('sale.order')
        self.res_user_obj = self.env['res.users']

    def test_sale_team_warehoue(self):
        '''
        1.- Testing that the Demo User has not sales team set.
        2.-Testing that the sales order created by Demo User has
        the main warehouse assigned by default.
        3.- Writting a sales team to Demo user and a default warehouse for
        the sales team realted to the Demo User.
        4.- Testing that the sales order created by Demo User after
        the sales team assignation has the default warehouse set
        on the user sales team.
        '''
        demo_user = self.env.ref('base.user_demo')
        main_wh = self.env.ref('stock.warehouse0')
        test_wh = self.env.ref('stock.stock_warehouse_shop0')
        sales_team = self.env.ref('sales_team.section_sales_department')
        self.assertFalse(demo_user.default_section_id.id,
                         'Demo User has assigned sales team.')
        sale = self.sale_obj.create(self.cr, demo_user.id, {
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
        })
        sale_brw = self.sale_obj.browse(self.cr, self.uid, sale)
        self.assertTrue(sale_brw.warehouse_id.id == main_wh.id,
                        'Default warehouse is not the main warehouse.')
        demo_user.write({'default_section_id': sales_team.id})
        sales_team.write({'default_warehouse': test_wh.id})
        sale = self.sale_obj.create(self.cr, demo_user.id, {
            'name': 'Tests Sales Team Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
        })
        sale_brw = self.sale_obj.browse(self.cr, self.uid, sale)
        self.assertTrue(sale_brw.warehouse_id.id == test_wh.id,
                        'Default warehouse is not the warehouse \
                        set on the sales team realted to de user.')
