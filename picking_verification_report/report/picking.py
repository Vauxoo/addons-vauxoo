# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.report import report_sxw


class packing_list_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(packing_list_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal': self._get_qtytotal,
        })

    def _get_qtytotal(self, move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total += move.product_qty
        return {'quantity': total, 'uom': uom}

report_sxw.report_sxw('report.m321_reports.packing_list_report',
                      'stock.picking',
                      'addons/m321_reports/report/picking.rml',
                      parser=packing_list_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
