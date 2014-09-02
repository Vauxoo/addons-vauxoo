#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp.tests.common import TransactionCase
from openerp.exceptions import AccessError
from openerp.osv.orm import except_orm
from openerp import SUPERUSER_ID
import mock
from openerp.addons.invoice_datetime.invoice import account_invoice
from openerp.tools import mute_logger
import pytz
import time
import datetime

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
        # I generate object of type datetime to send at function _get_datetime_with_user_tz
        datetime_object = datetime.datetime.strptime(dt_server,
                                                     '%Y-%m-%d %H:%M:%S')
        # create list with tz to apply in datetime
        tz_to_user = ['America/Caracas', 'America/Mexico_City']
        for tz in tz_to_user:
            self.user.write(cr, uid, uid, {'tz': tz}) #Assign tz to user
            #call the function _get_datetime_with_user_tz to get the date with tz applied
            datetime_tz = self.invoice._get_datetime_with_user_tz(cr, uid,
                                                             datetime_object)
            print datetime_tz, 'Datetime with tz: %s applied'%tz
        # Create an invoice with last tz of cycle America/Mexico_City
        res_id = self.invoice.create(cr, uid, {
                                                'partner_id':1,
                                                'account_id':1,
                                                'invoice_datetime': dt_server})
        dt_res = self.invoice.read(cr, uid, res_id, []).get('date_invoice_tz')
        # compare date calculated with function vs date of invoice record .
        self.assertEquals(datetime_tz,
                 dt_res, 'Date calculated and date of invoice are not equals')
