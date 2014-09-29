#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angélicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernande
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
#    You should have received a copy of the Affero GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import time
from openerp_print import report_sxw_ext  # nuevo
#~ from report_sxw_ext import report_sxw_ext #nuevo
# from report import report_sxw #original
from numero_a_texto import Numero_a_Texto


class report_check_voucher_pay(report_sxw_ext.rml_parse):  # nuevo
# class report_check_voucher_pay(report_sxw.rml_parse): #original

    def __init__(self, cr, uid, name, context):
        super(report_check_voucher_pay, self).__init__(
            cr, uid, name, context=context)
        self.contecito = context
        self.localcontext.update({
            'time': time,
            'obt_texto': self.obt_texto,
            'get_beneficiario': self.get_beneficiario,
            'get_monto': self.get_monto,
            'get_fecha': self.get_fecha,
        })

    def obt_texto(self):
        cantidad = self.contecito['amount']
        res = Numero_a_Texto(cantidad)
        return res

    def get_beneficiario(self, id_obj):
        payee = self.contecito['payee_id']
        partner = self.contecito['partner_id']
        if self.contecito['payee_id']:  # si existe un beneficiario se toma este si no se toma la comania
            ir_objj = self.pool.get('res.partner.address')
            s = ir_objj.browse(self.cr, self.uid, payee, context=None).name
            resultado = s.encode('"utf−8"')
            resultado = resultado.replace("á", 'Á')
            resultado = resultado.replace("é", 'É')
            resultado = resultado.replace("í", 'Í')
            resultado = resultado.replace("ó", 'Ó')
            resultado = resultado.replace("ú", 'Ú')
            resultado = resultado.replace("ñ", 'Ñ')

        else:
            ir_objj = self.pool.get('res.partner')
            s = ir_objj.browse(self.cr, self.uid, partner, context=None).name
            resultado = s.encode('"utf−8"')
            resultado = resultado.replace("á", 'Á')
            resultado = resultado.replace("é", 'É')
            resultado = resultado.replace("í", 'Í')
            resultado = resultado.replace("ó", 'Ó')
            resultado = resultado.replace("ñ", 'Ñ')
        return resultado.upper()

    def get_monto(self):
        monto = self.contecito['amount']
        return monto

    def get_fecha(self):
        date = []
        fecha = self.contecito[
            'date']  # fecha de la orden de pago, puede ser posdatada
        dia = fecha[8:10]
        mes = fecha[5:7]
        ano = fecha[0:4]
        if mes == "01":
            m = "ENERO"
        if mes == "02":
            m = "FEBRERO"
        if mes == "03":
            m = "MARZO"
        if mes == "04":
            m = "ABRIL"
        if mes == "05":
            m = "MAYO"
        if mes == "06":
            m = "JUNIO"
        if mes == "07":
            m = "JULIO"
        if mes == "08":
            m = "AGOSTO"
        if mes == "09":
            m = "SEPTIMBRE"
        if mes == "10":
            m = "OCTUBRE"
        if mes == "11":
            m = "NOVIEMBRE"
        if mes == "12":
            m = "DICIEMBRE"
        res = "CARACAS, %s DE %s" % (dia, m)
        date.append(res)
        date.append(ano)
        return date
report_sxw_ext.report_sxw(  # nuevo
    # report_sxw.report_sxw( #original
    'report.check_print_ext',
    'voucher.pay.support.wizard',
    'addons/bank_print_report/report/check.rml',
    parser=report_check_voucher_pay,
    header=False
)
