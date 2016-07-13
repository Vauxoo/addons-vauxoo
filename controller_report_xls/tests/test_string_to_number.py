# coding: utf-8

from openerp.tests.common import TransactionCase
from openerp.addons.controller_report_xls.controllers.main \
    import string_to_number, get_value, is_number, is_string, \
    is_formatted_number, get_xls
import logging
import tempfile
import os
import xlrd

_logger = logging.getLogger(__name__)


class TestController(TransactionCase):

    def setUp(self):
        super(TestController, self).setUp()
        # Asume lang = en_US
        self.lang_en_us = {
            'decimal_point': '.',
            'thousands_sep': ',',
        }
        self.lang_es_es = {
            'decimal_point': ',',
            'thousands_sep': '.',
        }
        self.value_en_us = u'-7,777,777.77'
        self.value_es_es = u'-7.777.777,77'
        self.value_text = u'a-7.777.777,77'
        self.result = -7777777.77
        self.html_snippet = '''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Vauxoo</title>
                </head>
                <body class="container">
                    <div class="header">
                        <table id="table_header">
                            <tr>
                                <td>Vauxoo</td>
                            </tr>
                        </table>
                    </div>
                    <div class="page">
                        <table id="table_body">
                            <thead>
                                <tr>
                                    <td>CODE</td>
                                    <td>ACCOUNT</td>
                                    <td>BALANCE</td>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>x2000</td>
                                    <td>Creditors - (Vx_Afr)</td>
                                    <td>%s</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="footer">
                        <table>
                            <tr>
                                <td>Vauxoo&#39;s Footer</td>
                            </tr>
                        </table>
                    </div>
                </body>
            </html>
        '''

    def test_get_value(self):
        res = get_value('-77')
        self.assertEqual(res, -77, 'Expected result -77')
        res = get_value('-77.7')
        self.assertEqual(res, -77.7, 'Expected result -77.7')
        res = get_value('-7.7.-')
        self.assertEqual(res, '-7.7.-', 'Expected result "-7.7.-"')

    def test_is_number(self):
        res = is_number('-77.7')
        self.assertEqual(res, True, 'Expected result True')
        res = is_number('-7.7.-')
        self.assertEqual(res, False, 'Expected result False')

    def test_is_string(self):
        res = is_string('a -77.7')
        self.assertEqual(res, True, 'Expected result True')
        res = is_string('/-77.7?')
        self.assertEqual(res, True, 'Expected result True')
        res = is_string('-7.7.-')
        self.assertEqual(res, True, 'Expected result True')
        res = is_string('-7.7.')
        self.assertEqual(res, True, 'Expected result True')
        res = is_string('7-7')
        self.assertEqual(res, True, 'Expected result True')
        res = is_string('-77.7')
        self.assertEqual(res, False, 'Expected result False')

    def test_is_formatted_number(self):
        res = is_formatted_number(self.value_text)
        self.assertEqual(res, False, 'Expected result False')
        res = is_formatted_number(self.value_en_us)
        self.assertEqual(res, True, 'Expected result True')

    def test_string_to_number_en_US(self):
        res = string_to_number(self.value_en_us, self.lang_en_us)
        self.assertEqual(res, self.result, 'Result not expected for en_US')

    def test_string_to_number_es_ES(self):
        res = string_to_number(self.value_es_es, self.lang_es_es)
        self.assertEqual(res, self.result, 'Result not expected for es_ES')

    def test_string_to_number_text(self):
        res = string_to_number(self.value_text, self.lang_es_es)
        self.assertEqual(res, self.value_text, 'Result not expected for es_ES')
        res = string_to_number(self.value_text, self.lang_en_us)
        self.assertEqual(res, self.value_text, 'Result not expected for en_US')

    def test_get_xls_es_es(self):
        xls_stream = get_xls(
            self.html_snippet % self.value_es_es, self.lang_es_es)
        fileno, fname = tempfile.mkstemp('.xls', 'controller.xls')
        with open(fname, "wb") as fobj:
            fobj.write(xls_stream)
        os.close(fileno)
        book = xlrd.open_workbook(fname)
        sh = book.sheet_by_index(0)
        self.assertEquals(sh.cell(0, 0).value, 'Vauxoo', 'Should be Vauxoo')
        self.assertEquals(sh.cell(3, 2).value, self.result, 'Wrong Value')

    def test_get_xls_en_us(self):
        xls_stream = get_xls(
            self.html_snippet % self.value_en_us)
        fileno, fname = tempfile.mkstemp('.xls', 'controller.xls')
        with open(fname, "wb") as fobj:
            fobj.write(xls_stream)
        os.close(fileno)
        book = xlrd.open_workbook(fname)
        sh = book.sheet_by_index(0)
        self.assertEquals(sh.cell(0, 0).value, 'Vauxoo', 'Should be Vauxoo')
        self.assertEquals(sh.cell(3, 2).value, self.result, 'Wrong Value')

    def test_get_xls_wrong(self):
        xls_stream = get_xls(
            self.html_snippet % self.value_en_us, self.lang_es_es)
        fileno, fname = tempfile.mkstemp('.xls', 'controller.xls')
        with open(fname, "wb") as fobj:
            fobj.write(xls_stream)
        os.close(fileno)
        book = xlrd.open_workbook(fname)
        sh = book.sheet_by_index(0)
        self.assertEquals(sh.cell(0, 0).value, 'Vauxoo', 'Should be Vauxoo')
        self.assertNotEquals(sh.cell(3, 2).value, self.result, 'Wrong Value')
        self.assertEquals(sh.cell(3, 2).value, self.value_en_us, 'Wrong Value')
