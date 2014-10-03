# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
# Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>   #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve            #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################
from openerp.report import report_sxw


class m321_c_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(m321_c_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date': self._get_date,
            'get_wh': self._get_wh,
        })

    def _get_date(self, obj, aux):
        aux2 = obj.date_invoice
        DMY = str(aux2)
        res = DMY.split('/')
        if aux == 0:
            return res[0]
        if aux == 1:
            return res[1]
        if aux == 2:
            return res[2]

    def _get_wh(self, obj):
        wh_ids = obj.tax_line
        aux = []
        for wh in wh_ids:
            aux.append(wh.tax_id.amount*100)
        return aux[0]

report_sxw.report_sxw(
    'report.m321_reports.m321_c_report',
    'account.invoice',
    'addons/m321_reports/report/amd_computadoras_report.rml',
    parser=m321_c_report,
    header=False
)
  # 1 addons/nombre del modulo/carpeta(report)/nombre del archivo rml
  # 2 A modo didactico vamos a poner que el modulo al que le vamos a poner el reporte es a res.partner
  #   pero podria ser cualquier modulo.
