#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import time
from openerp.report import report_sxw


class stock_valued(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(stock_valued, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_alicuota': self._get_alicuota,
            'get_rif': self._get_rif
        })

    def _get_alicuota(self, tnom=None):
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr, self.uid, [('name', '=', tnom)])
        if not tax_ids:
            tax_ids = tax_obj.search(self.cr, self.uid, [
                                     ('description', '=', tnom)])
        tax = tax_obj.browse(self.cr, self.uid, tax_ids)[0]
        return tax.amount * 100

    def _get_rif(self, vat=''):
        if not vat:
            return []
        return vat[2:].replace(' ', '')


report_sxw.report_sxw(
    'report.stock.guia_ve',
    'stock.picking',
    'addons/l10n_ve_stock/report/guiadespacho.rml',
    parser=stock_valued,
    header=False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
