# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
import time
from openerp.tools import mute_logger
from openerp.tests.common import TransactionCase
from openerp.tools.safe_eval import safe_eval


class TestWizardUpdateStandardPrice(TransactionCase):

    def setUp(self):
        super(TestWizardUpdateStandardPrice, self).setUp()
        self.cron_obj = self.env['ir.cron']
        self.wizard_obj = self.env['wizard.price']
        self.wiz_update = self.env['stock.change.standard.price']
        self.mrp_obj = self.env['mrp.bom']
        self.mrp_production_obj = self.env['mrp.production']
        self.w_upd_obj = self.env['stock.change.product.qty']
        self.move_obj = self.env['account.move']

        self.cron = self.env.ref(
            'product_extended_variants.ir_cron_module_update_cost_splited')
        self.prod = self.env.ref('product.product_product_5')
        self.mrp_bom = self.env.ref('mrp.mrp_bom_10')
        self.stock = self.env.ref('stock.stock_location_stock')

    def test_01_cron_splited_with_number_less_3(self):
        """Test with number parameter less that 3"""
        self.assertFalse(
            self.execute_cron_test(2), 'The cron was executed with number=2')

    def test_02_cron_splited_with_default_number(self):
        """Test cron without send the parameter number, to use default value"""
        self.assertTrue(self.execute_cron_test(), 'The cron was not executed')

    def test_03_create_several_crons(self):
        """Test to create crons to 43 products,
        check that only one is active"""
        self.mrp_bom.write({'product_id': self.prod.id})
        self.create_mrps(43)
        self.execute_cron_test(5)
        crons = self.cron_obj.search([
            ('model', '=', 'wizard.price'),
            ('name', 'ilike', 'Update Cost'),
        ])
        first = [cron for cron in crons if not safe_eval(cron.args)[1]]
        self.assertEquals(
            len(first), 1, 'More of one cron initial or not defined')
        args = safe_eval(first[0].args)
        ctx = {
            'active_ids': args[0],
            'active_id': args[0][0]
        }
        wiz = self.wizard_obj.with_context(ctx).create({})
        wiz.execute_cron(args[0], args[1], args[2])
        next_cron = self.cron_obj.browse(args[2])
        self.assertEquals(next_cron.active, True, 'Next cron no actived')

    def test_04_check_price_updated(self):
        """Run cron, and check that price is updated"""
        self.prod.write({'standard_price': 0.0})
        self.execute_cron_test()
        old = self.prod.standard_price
        ctx = {'active_id': self.prod.id}
        wiz = self.wizard_obj.with_context(ctx).create({})
        wiz.with_context({}).execute_cron([self.prod.id])
        self.assertNotEquals(
            old, self.prod.standard_price, 'No updated standard price')

    def test_05_run_cron_without_products(self):
        """Run cron without mrp's"""
        mrp_ids = self.mrp_obj.search([])
        mrp_ids.write({'active': False})
        self.assertFalse(
            self.execute_cron_test(), "Cron run with inactive mrp's")

    def test_06_product_real_cost_method(self):
        """Run cron, with product cost method as real"""
        self.prod.write({
            'standard_price': 0.0,
            'cost_method': 'real'})
        self.execute_cron_test()
        old = self.prod.standard_price
        ctx = {'active_id': self.prod.id}
        wiz = self.wizard_obj.with_context(ctx).create({})
        wiz.with_context({}).execute_cron([self.prod.id])
        self.assertEquals(
            old, self.prod.standard_price,
            'Updated standard price, with real cost')

    def test_07_check_decrements_price(self):
        """Decrements price in product"""
        self.prod.write({'standard_price': 10000.0})
        self.execute_cron_test()
        old = self.prod.standard_price
        ctx = {'active_id': self.prod.id}
        wiz = self.wizard_obj.with_context(ctx).create({})
        with mute_logger(
                'openerp.addons.product_extended_variants.wizard.wizard_price'
                ):
            wiz.with_context({}).execute_cron([self.prod.id])
        self.assertNotEquals(
            old, self.prod.standard_price, 'No updated standard price')

    def test_08_run_last_cron(self):
        """Test to create crons to 35 products, and execute last."""
        self.mrp_bom.write({'product_id': self.prod.id})
        self.create_mrps(35)
        self.execute_cron_test(5)
        crons = self.cron_obj.search([
            ('model', '=', 'wizard.price'),
            ('name', 'ilike', 'Update Cost'),
            ('active', '=', False),
        ])
        last = [cron for cron in crons if not safe_eval(cron.args)[2]]
        args = safe_eval(last[0].args)
        previous_cron = self.cron_obj.browse(args[1])
        previous_cron.write({'active': True})
        ctx = {
            'active_ids': args[0],
            'active_id': args[0][0]
        }
        wiz = self.wizard_obj.with_context(ctx).create({})
        wiz.execute_cron(args[0], args[1], args[2])
        self.assertFalse(previous_cron.active, 'Previous cron not deactivated')

    def test_09_update_product_price_with_wizard(self):
        current_price = self.prod.standard_price
        self.prod.write({
            'property_stock_account_input': self.env.ref('account.o_expense'),
            'property_stock_account_output': self.env.ref('account.o_income')
        })
        wizard_id = self.env['stock.change.standard.price'].with_context({
            'active_model': self.prod._name,
            'active_id': self.prod.id,
            'active_ids': self.prod.ids,
        }).create({'new_price': current_price})
        wizard_id.change_price()
        self.assertEqual(self.prod.standard_price, current_price,
                         'Product price was changed.')

    def test_10_update_product_price_with_wizard_with_qty(self):
        new_price = 1000
        self.prod.write({
            'property_stock_account_input': self.env.ref('account.o_expense'),
            'property_stock_account_output': self.env.ref('account.o_income'),
            'property_account_creditor_price_difference': self.env.ref(
                'account.stk')
        })
        self.w_upd_obj.create({
            'product_id': self.prod.id,
            'location_id': self.stock.id,
            'new_quantity': 18,
            }).change_product_qty()
        wizard_id = self.env['stock.change.standard.price'].with_context({
            'active_model': self.prod._name,
            'active_id': self.prod.id,
            'active_ids': self.prod.ids,
        }).create({'new_price': new_price})
        wizard_id.change_price()
        ref = '[{code}] {name}' % dict(
            code=self.prod.default_code, name=self.prod.name)
        move = self.move_obj.search([('ref', '=', ref)])
        self.assertTrue(move.ids, 'Movement not created.')

    def create_mrps(self, qty_to_create):
        """Create many mrps, to tests
        qty_to_create = Qty of products and mrp to create"""
        for number in range(0, qty_to_create):
            new_prod = self.prod.copy(
                {'name': ('%s - %s', (self.prod.name, number))})
            self.mrp_bom.copy({
                'product_tmpl_id': new_prod.product_tmpl_id.id,
                'product_id': new_prod.id
            })

    def execute_cron_test(self, number=False):
        self.cron.write({
            'nextcall': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'args': ('(%s)' % (number and (str(number) + ',') or '')),
        })
        ctx = dict(self.env.context)
        ctx.pop('active_test', None)
        method = getattr(
            self.cron_obj.with_context(ctx).env[self.cron.model],
            self.cron.function)
        args = safe_eval('tuple(%s)' % (self.cron.args or ''))
        return method(*args)
