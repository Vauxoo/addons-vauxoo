from openerp import SUPERUSER_ID
from openerp.osv.orm import except_orm
from openerp.tests.common import TransactionCase
import time
from openerp.tools.misc import mute_logger
from openerp.tests import common
UID = common.ADMIN_USER_ID
DB = common.DB
from datetime import date


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

    @mute_logger('openerp.addons.account_user_audit.tests.test_group',
                 'openerp.osv.orm',
                 'openerp.addons.base.ir.ir_model',
                 'openerp.models')
    def test_creates(self):
        """Test the create methods in account.invoice, account.move.line ..."""
        cr, uid = self.cr, self.uid
        # Search Auditor user
        utest = self.data.get_object_reference(
            cr, uid, "account_user_audit", "res_auditor_user")
        # Create an invoice with Test user, most fail
        with self.assertRaises(except_orm) as cm:
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
        print "----CORRECTO : Factura no Creada", cm.exception
        # Create Journal Entries with Test user, most fail
        # import pdb; pdb.set_trace()
        with self.assertRaises(except_orm)as cm:
            self.account_move.create(
                cr, utest[1],
                {'name': '/',
                 'period_id': self.period_9_id,
                 'journal_id': self.sale_journal_id,
                 'date': date.today(),
                 'line_id': [(0, 0, {'name': 'foo', 'debit': 10, }),
                             (0, 0, {'name': 'bar', 'credit': 10, })]
                 })
        print "----CORRECTO : Account_move no Creada", cm.exception

        # Create Journal Item with test user, most fail.
        move_id = self.account_move.create(
            cr, SUPERUSER_ID,
            {'name': '/',
             'period_id': self.period_9_id,
             'journal_id': self.sale_journal_id,
             'date': date.today(),
             })

        with self.assertRaises(except_orm)as cm:
            self.move_line_obj.create(
                cr, utest[1],
                {'move_id': move_id,
                 'name': '/',
                 'debit': 0,
                 'credit': 100,
                 'account_id': self.ref('account.a_sale')})
        print "----CORRECTO : Account_move_line no Creada", cm.exception

        # Create account.bank.statement with test user, most fail.
        with self.assertRaises(except_orm)as cm:
            self.bank_statement.create(
                cr, utest[1],
                {'journal_id': self.bank_journal_usd_id,
                 'date': time.strftime('%Y') + '-07-15', })
        print "----CORRECTO : bank_statement no Creada", cm.exception
