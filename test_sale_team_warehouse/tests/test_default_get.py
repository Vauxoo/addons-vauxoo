# coding: utf-8

from openerp.tests.common import TransactionCase


class TestDefaultGet(TransactionCase):

    def setUp(self):
        super(TestDefaultGet, self).setUp()
        self.generic_model_obj = self.env['test.generic.model']
        self.default_get_model_obj = self.env['test.default.get.model']
        self.warehouse_obj = self.env['stock.warehouse']
        self.default_get_warehouse_model_obj = self.env[
            'test.default.get.warehouse.model']

    def tests_default_get_model(self):
        """1.- Testing the default basic method.
        2.- Testing that the overwriting default_get works.
        3.- Testing that the record warehouse_id match with the
        warehouse returned for the _default_warehouse method.
        4.- Testing that the record warehouse_id match with the
        warehouse_id assign on the sales team of the user.
        """
        record = self.generic_model_obj.create({'name': 'TestName1'})
        self.assertTrue(record.character == 'Test Default Chart',
                        'Default character text is not set.')
        record = self.default_get_model_obj.create({'name': 'TestName2'})
        self.assertTrue(record.character == 'Demo Text For Test Purposes',
                        'Default character text is not set.')
        record = self.default_get_warehouse_model_obj.create({'name':
                                                              'TestName3'})
        user = self.env.ref('base.user_root')
        res = self.warehouse_obj.search([('company_id', '=',
                                          user.company_id.id)],
                                        limit=1)
        self.assertTrue(res.id == record.warehouse_id.id,
                        'The record warehouse_id is not the same that the\
                        _default_warehouse method returns.')

        sales_team = self.env.ref('sales_team.section_sales_department')
        test_wh = self.env.ref('stock.stock_warehouse_shop0')
        user.write({'default_section_id': sales_team.id})
        sales_team.write({'default_warehouse': test_wh.id})
        record = self.default_get_warehouse_model_obj.create({'name':
                                                              'TestName4'})
        self.assertTrue(record.warehouse_id.id == test_wh.id,
                        'The record warehouse_id is not the same that the\
                        assign on the sales team of the user.')
