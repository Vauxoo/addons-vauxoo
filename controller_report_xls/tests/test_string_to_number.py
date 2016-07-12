# coding: utf-8

from openerp.tests.common import TransactionCase
from openerp.addons.controller_report_xls.controllers.main \
    import string_to_number
import logging

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
        self.value_en_US = u'-7,777,777.77'
        self.value_es_ES = u'-7.777.777,77'
        self.value_text = u'a-7.777.777,77'
        self.result = -7777777.77

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
