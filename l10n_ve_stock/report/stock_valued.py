# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw

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
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])
        if not tax_ids:
            tax_ids = tax_obj.search(self.cr,self.uid,[('description','=',tnom)])
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)[0]
        return tax.amount*100


    def _get_rif(self, vat=''):
        if not vat:
            return []
        return vat[2:].replace(' ', '')




report_sxw.report_sxw(
    'report.stock.valued_ve',
    'stock.picking',
    'addons/l10n_ve_stock/report/albaran.rml',
    parser=stock_valued,
    header=False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
