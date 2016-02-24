# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Osval Reyes <osval@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tests.common import TransactionCase
from lxml import html


class TestPrintSummaryReport(TransactionCase):

    def setUp(self):
        super(TestPrintSummaryReport, self).setUp()
        self.claim_id = self.ref("crm_claim.crm_claim_6")
        self.claim_ids = self.env['crm.claim'].browse(self.claim_id)
        self.report_name = 'crm_claim_summary_report.report_translated'

    def call_qweb_report(self, claim_ids):
        '''
        This function serve as a wrapper for report call when printing
        '''
        return self.env['report'].\
            get_action(claim_ids, self.report_name)

    def print_html_qweb_report(self, claim_ids):
        '''
        This function serve as a wrapper when printing a report in html format
        '''
        return self.env['report'].get_html(claim_ids, self.report_name)

    def test_01_print_report_call(self):
        res = self.call_qweb_report(self.claim_ids)

        self.assertTrue(res and res['context'] and
                        res['context']['active_ids'])
        self.assertEqual(res['context']['active_ids'], [self.claim_id])

    def test_02_get_html(self):
        content = html.document_fromstring(
            self.print_html_qweb_report(self.claim_ids))

        css_html_tree = content.xpath("//html/head/link[@rel='stylesheet']")
        css_files = [html.tostring(css_file).strip()
                     for css_file in css_html_tree]

        self.assertEqual(len(css_files), 3, "Report has no CSS files loaded")
