# coding: utf-8
###########################################################################
#    Module Writen to ODOO, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
##############################################################################
from openerp.addons.aging_due_report.tests.common import TestAgingCommon
from openerp.addons.controller_report_xls.controllers.main import get_xls
import logging
from openerp import workflow
import openerp
import base64
import os
import xlrd
import tempfile

_logger = logging.getLogger(__name__)


class TestReportAging(TestAgingCommon):

    def setUp(self):
        super(TestReportAging, self).setUp()

    def test_report_againg_partner(self):
        _logger.info('I generate register to get in report')
        self._generate_register()
        _logger.info('I generate the report again supplier')
        self._generate_report_againg()
        _logger.info('I generate the detailed report supplier')
        self._generate_report_detailed()

    def _generate_register(self):
        invoice_id = self.invoice_demo.copy(
            {'partner_id': self.partner_id.id,
             'check_total': self.invoice_demo.amount_total})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice_id.id, 'invoice_open',
            self.cr)

    def _generate_report_detailed(self):
        wiz_id = self.wiz_aging_obj.create({
            'result_selection': 'supplier',
            'report_format': 'xls',
            'type': 'detail',
        })
        context = {
            'report_name': 'aging_due_report.detail_due_report_qweb',
            'rows': 7
        }
        self._create_report(wiz_id, context=context)

    def _generate_report_againg(self):
        wiz_id = self.wiz_aging_obj.create({
            'result_selection': 'supplier',
            'direction': 'past',
            'report_format': 'xls',
            'type': 'aging',
            'period_length': 30,
        })
        context = {
            'report_name': 'aging_due_report.aging_due_report_qweb',
            'rows': 5
        }
        self._create_report(wiz_id, context=context)

    def _create_report(self, wiz_id, context=None):
        if context is None:
            context = {}
        context.update({
            'xls_report': True,
            'active_model': 'res.partner',
            'active_ids': [self.partner_id.id],
            'active_id': self.partner_id.id,
        })
        data = wiz_id.with_context(context).print_report()
        context.update({
            'active_model': 'account.aging.wizard',
            'active_ids': [wiz_id.id],
            'active_id': wiz_id.id,
        })
        result = openerp.report.render_report(
            self.cr, self.uid, [wiz_id.id],
            context.get('report_name', ''), data.get('data', {}),
            context=context)[0]
        report = get_xls(result)
        attach = self.attachment_obj.create({
            'name': 'xls_aging_supplier',
            'datas_fname': 'xls_aging_supplier.xls',
            'datas': base64.encodestring(report),
            'res_model': 'account.aging.wizard',
            'res_id': wiz_id.id})
        self._check_file_xls(attach, context=context)

    def _check_file_xls(self, attachment, context=None):
        _logger.info('I check that file is correct')
        (fileno, fname) = tempfile.mkstemp('.xls', 'xls_aging_supplier.xls')
        with open(fname, "wb") as fobj:
            fobj.write(base64.decodestring(attachment.datas))
        os.close(fileno)
        file_xls = fname
        book = xlrd.open_workbook(file_xls)
        sh = book.sheet_by_index(0)
        self.assertEquals(
            sh.nrows, context.get('rows', 0),
            'the generated file contains more or less lines than expected')
