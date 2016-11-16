# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import datetime
import logging
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger
_logger = logging.getLogger(__name__)


class TestInvoiceDatetime(TransactionCase):

    def setUp(self):
        super(TestInvoiceDatetime, self).setUp()
        self.user = self.registry('res.users')
        self.data = self.registry('ir.model.data')
        self.invoice = self.registry('account.invoice')

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_get_datetime(self):
        cr, uid = self.cr, self.uid
        # get datetime of server in string
        dt_server = time.strftime('%Y-%m-%d %H:%M:%S')
        # I generate object of type datetime
        # to send at function _get_datetime_with_user_tz
        datetime_object = datetime.datetime.strptime(dt_server,
                                                     '%Y-%m-%d %H:%M:%S')
        # create list with tz to apply in datetime
        self.user.write(cr, uid, uid, {'tz': 'Europe/Rome'})
        # Assign tz to user
        # call the function _get_datetime_with_user_tz
        # to get the date with tz applied
        datetime_tz_rome = self.invoice._get_datetime_with_user_tz(
            cr, uid, datetime_object)
        # Create an invoice with last tz of cycle America/Mexico_City
        invoice_tz_rome_id = self.invoice.create(
            cr, uid,
            {'partner_id': 1,
             'account_id': 1,
             'invoice_datetime': dt_server})
        self.user.write(cr, uid, uid, {'tz': 'America/Mexico_City'})
        # Assign tz to user
        datetime_tz_mx = self.invoice._get_datetime_with_user_tz(
            cr, uid, datetime_object)
        invoice_tz_mx_id = self.invoice.create(
            cr, uid,
            {'partner_id': 1,
             'account_id': 1,
             'invoice_datetime': dt_server})
        dt_inv_tz_rome = self.invoice.read(
            cr, uid, invoice_tz_rome_id, []).get('date_invoice_tz')
        dt_inv_tz_mx = self.invoice.read(
            cr, uid, invoice_tz_mx_id, []).get('date_invoice_tz')
        _logger.info("Validate datetime of function, for Rome-Mexico_City TZ")
        self.assertNotEqual(
            datetime_tz_rome,
            datetime_tz_mx, 'Dates are equal, should be different')
        _logger.info("Validate datetime of function versus invoice datetime")
        self.assertEquals(datetime_tz_rome, dt_inv_tz_rome,
                          'Date calculated and date of invoice are not equals')
        self.assertEquals(datetime_tz_mx, dt_inv_tz_mx,
                          'Date calculated and date of invoice are not equals')
        _logger.info("Validate invoice datetime, for Rome-Mexico_City TZ")
        self.assertNotEqual(
            dt_inv_tz_rome,
            dt_inv_tz_mx, 'Dates are equal, must be different on invoices')
