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
import time
from openerp.report import report_sxw
from openerp.tools.translate import _


class cm321_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(cm321_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                                 'get_discount': self._get_discount,
                                 'get_date': self._get_date,
                                 'get_wh': self._get_wh,
                                 })

    def _get_discount(self, obj):
        aux = 100
        aux2 = 0.0
        ppv = self.pool.get('product.pricelist.version')
        date_invoice = str(obj.date_invoice)
        if obj.type == 'out_invoice':
            price_list = obj.partner_id.property_product_pricelist
            if price_list.active:
                ppv_ids = price_list.version_id
                for ppv in ppv_ids:
                    if ppv.date_start and ppv.date_end:
                        date_start = str(ppv.date_start)
                        date_end = str(ppv.date_end)
                        if ppv.date_start <= obj.date_invoice and\
                                            obj.date_invoice <= ppv.date_end:
                            ppli = ppv.items_id
                            for ppl in ppli:
                                if ppl.sequence < aux:
                                    aux = ppl.sequence
                                    aux2 = ppl.price_discount
                            return aux2*100
                        else:
                            return aux2
                    else:
                        return aux2
        else:
            price_list = obj.partner_id.property_product_pricelist_purchase
            if price_list.active:
                ppv_ids = price_list.version_id
                for ppv in ppv_ids:
                    if ppv.date_start and ppv.date_end:
                        date_start = str(ppv.date_start)
                        date_end = str(ppv.date_end)
                        if ppv.date_start <= obj.date_invoice and\
                                            obj.date_invoice <= ppv.date_end:
                            ppli = ppv.items_id
                            for ppl in ppli:
                                if ppl.sequence < aux:
                                    aux = ppl.sequence
                                    aux2 = ppl.price_discount
                            return aux2*100
                        else:
                            return aux2
                    else:
                        return aux2
        return aux2

    def _get_date(self, obj, aux):
        aux2 = obj.date_invoice
        DMY = str(aux2)
        res = DMY.split('/')
        if aux == 0:
            return res[0]
        if aux == 1:
            return res[1]
        if aux == 2:
            return res[2][0:4]

    def _get_wh(self, obj):
        wh_ids = obj.tax_line
        aux = []
        for wh in wh_ids:
            aux.append(wh.tax_id.amount*100)
        return aux[0]

report_sxw.report_sxw(
    'report.m321_reports.cm321_report',
    'account.invoice',
    'addons/m321_reports/report/comercializadora_m321_report.rml',
    parser=cm321_report
)
  # 1 addons/nombre del modulo/carpeta(report)/nombre del archivo rml
  # 2 A modo didactico vamos a poner que el modulo al que le vamos a poner el reporte es a res.partner
  #   pero podria ser cualquier modulo.
