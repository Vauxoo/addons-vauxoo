# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
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

import time

from openerp.osv import osv
from openerp.report import report_sxw


class StockAccrualParser(report_sxw.rml_parse):
    _name = 'stock.accrual.parser'

    def __init__(self, cr, uid, name, context=None):
        super(StockAccrualParser, self).__init__(cr, uid, name,
                                                 context=context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context


class IfrsPortraitPdfReport(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="stock_accrual_report.stock_accrual_report_name"
    _name = 'report.stock_accrual_report.stock_accrual_report_name'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'stock_accrual_report.stock_accrual_report_template'
    _wrapped_report_class = StockAccrualParser
