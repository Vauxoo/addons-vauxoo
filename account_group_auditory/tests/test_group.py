# coding: utf-8
import time
from datetime import date

from openerp import SUPERUSER_ID
from openerp.osv.orm import except_orm
from openerp.tests import common
from openerp.tests.common import TransactionCase
from openerp.tools.misc import mute_logger

UID = common.ADMIN_USER_ID
DB = common.DB


class TestAuditorGroup(TransactionCase):

    def setUp(self):
        super(TestAuditorGroup, self).setUp()
        self.data = self.registry('ir.model.data')
        self.invoice = self.registry('account.invoice')
        self.account_move = self.registry('account.move')
        self.move_line_obj = self.registry('account.move.line')
        self.bank_statement = self.registry('account.bank.statement')
        self.partner = self.registry('res.partner')
        self.users = self.registry('res.users')
        self.partner_agrolait_id = self.data.get_object_reference(
            self.cr, self.uid, "base", "res_partner_2")[1]
        self.currency_swiss_id = self.data.get_object_reference(
            self.cr, self.uid, "base", "CHF")[1]
        self.account_rcv_id = self.data.get_object_reference(
            self.cr, self.uid, "account", "a_recv")[1]
        self.product_id = self.data.get_object_reference(
            self.cr, self.uid, "product", "product_product_4")[1]
        self.period_9_id = self.data.get_object_reference(
            self.cr, self.uid, "account", "period_9")[1]
        self.sale_journal_id = self.data.get_object_reference(
            self.cr, self.uid, "account", "sales_journal")[1]
        self.bank_journal_usd_id = self.data.get_object_reference(
            self.cr, self.uid, "account", "bank_journal_usd")[1]

    @mute_logger('openerp.addons.account_group_auditory.tests.test_group',
                 'openerp.osv.orm',
                 'openerp.addons.base.ir.ir_model',
                 'openerp.models')
    def test_creates(self):
        """Test the create methods in account.invoice, account.move.line ..."""
        cr, uid = self.cr, self.uid
        # Search Auditor user
        utest = self.data.get_object_reference(
            cr, uid, "account_group_auditory", "res_auditor_user")
        # Create an invoice with Test user, most fail
        with self.assertRaises(except_orm):
            self.invoice.create(
                cr, utest[1],
                {'partner_id': self.partner_agrolait_id,
                 'reference_type': 'none',
                 'currency_id': self.currency_swiss_id,
                 'name': 'invoice to client',
                 'account_id': self.account_rcv_id,
                 'type': 'out_invoice',
                 # to use USD rate rateUSDbis
                 'date_invoice': time.strftime('%Y') + '-07-01',
                 })
        # Create Journal Entries with Test user, most fail
        with self.assertRaises(except_orm):
            self.account_move.create(
                cr, utest[1],
                {'name': '/',
                 'period_id': self.period_9_id,
                 'journal_id': self.sale_journal_id,
                 'date': date.today(),
                 'line_id': [(0, 0, {'name': 'foo', 'debit': 10, }),
                             (0, 0, {'name': 'bar', 'credit': 10, })]
                 })
        # Create Journal Item with test user, most fail.
        move_id = self.account_move.create(
            cr, SUPERUSER_ID,
            {'name': '/',
             'period_id': self.period_9_id,
             'journal_id': self.sale_journal_id,
             'date': date.today(),
             })
        with self.assertRaises(except_orm):
            self.move_line_obj.create(
                cr, utest[1],
                {'move_id': move_id,
                 'name': '/',
                 'debit': 0,
                 'credit': 100,
                 'account_id': self.ref('account.a_sale')})
        # Create account.bank.statement with test user, most fail.
        with self.assertRaises(except_orm):
            self.bank_statement.create(
                cr, utest[1],
                {'journal_id': self.bank_journal_usd_id,
                 'date': time.strftime('%Y') + '-07-15', })
        # Create Custumer or supplier (res.partner), most to fail
        with self.assertRaises(except_orm):
            self.partner.create(cr, utest[1], {'name': 'MyPartner1'})

    @mute_logger('openerp.addons.account_group_auditory.tests.test_group',
                 'openerp.osv.orm',
                 'openerp.addons.base.ir.ir_model',
                 'openerp.models')
    def test_unlink(self):
        """Test the unlink methods in account.invoice, account.move.line ..."""
        cr, uid = self.cr, self.uid
        # Search Auditor user
        utest = self.data.get_object_reference(
            cr, uid, "account_group_auditory", "res_auditor_user")
        # Unlink an invoice with Test user, most fail
        invoice_id = self.invoice.create(
            cr, SUPERUSER_ID,
            {'partner_id': self.partner_agrolait_id,
             'reference_type': 'none',
             'currency_id': self.currency_swiss_id,
             'name': 'invoice to client',
             'account_id': self.account_rcv_id,
             'type': 'out_invoice',
             # to use USD rate rateUSDbis
             'date_invoice': time.strftime('%Y') + '-07-01', })
        with self.assertRaises(except_orm):
            self.invoice.unlink(cr, utest[1], [invoice_id])
        # unlink Custumer or supplier (res.partner), most to fail
        with self.assertRaises(except_orm):
            self.partner.unlink(cr, utest[1], [self.partner_agrolait_id])
        # unlink Journal Entries with Test user, most fail
        move_id = self.account_move.create(
            cr, SUPERUSER_ID,
            {'name': '/',
             'period_id': self.period_9_id,
             'journal_id': self.sale_journal_id,
             'date': date.today(),
             })
        with self.assertRaises(except_orm):
            self.account_move.unlink(cr, utest[1], [move_id])
        # Unlik Journal Item with test user, most fail.
        move_line_id = self.move_line_obj.create(
            cr, SUPERUSER_ID,
            {'move_id': move_id,
             'name': '/',
             'debit': 0,
             'credit': 100,
             'account_id': self.ref('account.a_sale')})
        with self.assertRaises(except_orm):
            self.move_line_obj.unlink(cr, utest[1], [move_line_id])
        bank_statement_id = self.bank_statement.create(
            cr, SUPERUSER_ID,
            {'journal_id': self.bank_journal_usd_id,
             'date': time.strftime('%Y') + '-07-15', })
        with self.assertRaises(except_orm):
            self.bank_statement.unlink(cr, utest[1], [bank_statement_id])

    @mute_logger('openerp.addons.account_group_auditory.tests.test_group',
                 'openerp.osv.orm',
                 'openerp.addons.base.ir.ir_model',
                 'openerp.models')
    def test_write(self):
        """Test the WRITE methods in account.invoice, account.move.line ..."""
        cr, uid = self.cr, self.uid
        # Search Auditor user
        utest = self.data.get_object_reference(
            cr, uid, "account_group_auditory", "res_auditor_user")

        invoice_id = self.invoice.create(
            cr, SUPERUSER_ID,
            {'partner_id': self.partner_agrolait_id,
             'reference_type': 'none',
             'currency_id': self.currency_swiss_id,
             'name': 'invoice to client',
             'account_id': self.account_rcv_id,
             'type': 'out_invoice',
             # to use USD rate rateUSDbis
             'date_invoice': time.strftime('%Y') + '-07-01', })
        move_id = self.account_move.create(
            cr, SUPERUSER_ID,
            {'name': '/',
             'period_id': self.period_9_id,
             'journal_id': self.sale_journal_id,
             'date': date.today(),
             })
        move_line_id = self.move_line_obj.create(
            cr, SUPERUSER_ID,
            {'move_id': move_id,
             'name': '/',
             'debit': 0,
             'credit': 100,
             'account_id': self.ref('account.a_sale')})
        bank_statement_id = self.bank_statement.create(
            cr, SUPERUSER_ID,
            {'journal_id': self.bank_journal_usd_id,
             'date': time.strftime('%Y') + '-07-15', })

        # write an invoice with Test user, most fail
        with self.assertRaises(except_orm):
            self.invoice.write(
                cr, utest[1], [invoice_id],
                {'name': 'invoice to TEST', })

        # write Custumer or supplier (res.partner), most to fail
        with self.assertRaises(except_orm):
            self.partner.write(cr, utest[1], [self.partner_agrolait_id],
                               {'name': 'TEST AGROlait'})

        # write Journal Entries with Test user, most fail
        with self.assertRaises(except_orm):
            self.account_move.write(cr, utest[1], [move_id], {'name': '/TEST'})

        # write Journal Item with test user, most fail.
        with self.assertRaises(except_orm):
            self.move_line_obj.write(
                cr, utest[1], [move_line_id], {'name': '/'})

        # write account.bank.statement with test user, most fail.
        with self.assertRaises(except_orm):
            self.bank_statement.unlink(
                cr, utest[1], [bank_statement_id],
                {'date': time.strftime('%Y') + '-09-15'})

    @mute_logger('openerp.addons.account_group_auditory.tests.test_group',
                 'openerp.osv.orm',
                 'openerp.addons.base.ir.ir_model',
                 'openerp.models')
    def test_read(self):
        """Test the READ methods in account.invoice, account.move.line ..."""
        cr, uid = self.cr, self.uid
        # Search Auditor user
        utest = self.data.get_object_reference(
            cr, uid, "account_group_auditory", "res_auditor_user")

        invoice_id = self.invoice.create(
            cr, SUPERUSER_ID,
            {'partner_id': self.partner_agrolait_id,
             'reference_type': 'none',
             'currency_id': self.currency_swiss_id,
             'name': 'invoice to client',
             'account_id': self.account_rcv_id,
             'type': 'out_invoice',
             # to use USD rate rateUSDbis
             'date_invoice': time.strftime('%Y') + '-07-01', })
        move_id = self.account_move.create(
            cr, SUPERUSER_ID,
            {'name': '/',
             'period_id': self.period_9_id,
             'journal_id': self.sale_journal_id,
             'date': date.today(),
             })
        move_line_id = self.move_line_obj.create(
            cr, SUPERUSER_ID,
            {'move_id': move_id,
             'name': '/',
             'debit': 0,
             'credit': 100,
             'account_id': self.ref('account.a_sale')})
        bank_statement_id = self.bank_statement.create(
            cr, SUPERUSER_ID,
            {'journal_id': self.bank_journal_usd_id,
             'date': time.strftime('%Y') + '-07-15', })
        # Read a partner most to success
        partner_obj = self.partner.browse(
            cr, SUPERUSER_ID, [self.partner_agrolait_id])
        partner_values, = self.partner.read(
            cr, utest[1], [self.partner_agrolait_id], ['name'])
        self.assertEqual(partner_obj.name, partner_values['name'])

        # Read an invoice,most success
        invoice_obj = self.invoice.browse(
            cr, SUPERUSER_ID, [invoice_id])
        invoice_values, = self.invoice.read(
            cr, utest[1], [invoice_id], ['name'])
        self.assertEqual(invoice_obj.name, invoice_values['name'])

        # Read a move
        move_obj = self.account_move.browse(
            cr, SUPERUSER_ID, [move_id])
        move_values, = self.account_move.read(
            cr, utest[1], [move_id], ['name'])
        self.assertEqual(move_obj.name, move_values['name'])

        # Read move_line
        move_line = self.move_line_obj.browse(
            cr, SUPERUSER_ID, [move_line_id])
        move_line_values, = self.move_line_obj.read(
            cr, utest[1], [move_line_id], ['name'])
        self.assertEqual(move_line.name, move_line_values['name'])

        # Read bank statement
        bank_statement_obj = self.bank_statement.browse(
            cr, SUPERUSER_ID, [bank_statement_id])
        bank_statement_values, = self.bank_statement.read(
            cr, utest[1], [bank_statement_id], ['date'])
        self.assertEqual(
            bank_statement_obj.date, bank_statement_values['date'])
