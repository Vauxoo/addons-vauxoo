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
from openerp.addons.product_pricelist_report_qweb.tests.common import\
    TestXLSProductCommon
from openerp.addons.controller_report_xls.controllers.main import get_xls
import logging
import openerp
import base64
import os
import xlrd
import tempfile

_logger = logging.getLogger(__name__)


class TestReportProductXls(TestXLSProductCommon):

    def setUp(self):
        super(TestReportProductXls, self).setUp()

    # def test_report_xls_product_pricelist(self):
    #     self.products_with_price = False
    #     self.columns_number = 11
    #     _logger.info('I generate the report xls for product price_list')
    #     self._generate_report_product()
    #     _logger.info(
    #         'I generate the report xls for product price_list witout price')
    #     self.products_with_price = True
    #     self.product.list_price = 0
    #     self.columns_number = 10
    #     self._generate_report_product()

    # def _generate_report_product(self):
    #     wiz_id = self.product_price_obj.create({
    #         'price_list': self.price_list_id,
    #         'qty1': 1,
    #         'qty2': 5,
    #         'qty3': 10,
    #         'qty4': 0,
    #         'qty5': 0,
    #         'report_format': 'xls',
    #         'products_with_price': self.products_with_price,
    #     })
    #     context = {
    #         'xls_report': True,
    #         'active_model': 'product.product',
    #         'active_ids': [self.product.id],
    #         'active_id': self.product.id,
    #     }
    #     data = wiz_id.with_context(context).print_report()
    #     result = openerp.report.render_report(
    #         self.cr, self.uid, [wiz_id.id],
    #         'product.report_pricelist', data.get('data', {}),
    #         context=context)[0]
    #     report = get_xls(result)
    #     attach = self.attachment_obj.create({
    #         'name': 'xls_product_price_list',
    #         'datas_fname': 'xls_product_price_list.xls',
    #         'datas': base64.encodestring(report),
    #         'res_model': 'product.price_list',
    #         'res_id': wiz_id.id})
    #     self._check_file_xls(attach)

    # def _check_file_xls(self, attachment, ):
    #     _logger.info('I check that file is correct')
    #     (fileno, fname) = tempfile.mkstemp('.xls', 'xls_aging_supplier.xls')
    #     with open(fname, "wb") as fobj:
    #         fobj.write(base64.decodestring(attachment.datas))
    #     os.close(fileno)
    #     file_xls = fname
    #     book = xlrd.open_workbook(file_xls)
    #     sh = book.sheet_by_index(0)
    #     self.assertEquals(
    #         sh.nrows, self.columns_number,
    #         'the generated file contains more or less lines than expected')
