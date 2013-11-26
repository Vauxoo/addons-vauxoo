#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################



from osv import osv, fields
import pooler
import time
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)

try:
    from account_financial_report.report import parser as Parser
except ImportError:
    _logger.warning("Please download module account_financial_report")



class wizard_report(osv.osv_memory):
    _inherit = "wizard.report"

    _columns = {
        'report_format' : fields.selection([
            ('pdf', 'PDF'),
            ('spreadsheet', 'Spreadsheet')], 'Report Format')
    }
    def get_parser_method(self, cr, uid, ids, method=None, args=None, param=None, context=None):
        if context is None:
            context = {}
        
        acc_bal_obj = Parser.account_balance(cr, uid, ids ,context=context)
        res = []

        if method:
            if method in ("get_company_accounts", "_get_analytic_ledger", "_get_journal_ledger",
                "lines"):
                res = getattr(acc_bal_obj, method)(args, param)
            else:
                res = getattr(acc_bal_obj, method)(args)

        return res

    def print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        
        res = super(wizard_report, self).print_report(cr, uid, ids, data=data, context=context)

        res.get('datas')['ids'] = ids

        if( res.get('report_name') == 'afr.1cols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_col1_html'
            else:
                res['report_name'] = 'afr_report_col1'
        
        if( res.get('report_name') == 'afr.2cols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_col2_html'
            else:
                res['report_name'] = 'afr_report_col2'

        if( res.get('report_name') == 'afr.4cols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_col4_html'
            else:
                res['report_name'] = 'afr_report_col4'
        
        if( res.get('report_name') == 'afr.5cols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_col5_html'
            else:
                res['report_name'] = 'afr_report_col5'
          
        if( res.get('report_name') == 'afr.journal.ledger'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_journal_ledger_html'
            else:
                res['report_name'] = 'afr_report_journal_ledger'
        
        if( res.get('report_name') == 'afr.analytic.ledger'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_analytic_ledger_html'
            else:
                res['report_name'] = 'afr_report_analytic_ledger'

        if( res.get('report_name') == 'afr.qtrcols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_qtr_html'
            else:
                res['report_name'] = 'afr_report_qtr'

        if( res.get('report_name') == 'afr.13cols'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_col13_html'
            else:
                res['report_name'] = 'afr_report_col13'
        if( res.get('report_name') == 'afr.partner.balance'):
            if (res.get('datas').get('form')['report_format'] == 'spreadsheet'):
                res['report_name'] = 'afr_report_partner_balance_html'
            else:
                res['report_name'] = 'afr_report_partner_balance'
        
        return res



