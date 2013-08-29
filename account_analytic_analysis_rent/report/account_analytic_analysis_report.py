# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    code by rod@vauxoo.com
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
import locale
import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _
class account_analytic_account_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_analytic_account_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'accesory': self._accesory,
            'type_payment' : self._type_payment,
            'get_data_features' : self._get_data_features,
            'get_type_features' : self._get_type_features,
            'locale_date' : self._locale_date,
        })
    def _accesory(self,product_id):
        if product_id.type == 'accesory':
            return product_id.product_id.name
        return []
    def _type_payment(self,feature_id):
        if feature_id.name and feature_id.name.name == 'Copias Bco y Negro' or feature_id.name.name == 'Copias Color' :
            return 'Por copia procesada'
        return 'Mensual'
    def _get_data_features(self, product_id, obj_features):
        list_data = []
        if product_id == obj_features.product_line_id.id:
            list_data.append(obj_features.product_line_id.name)
            list_data.append(obj_features.counter)
            list_data.append(obj_features.name.name)
            list_data.append(obj_features.cost)
            return list_data
        return ['','','','']
    def _get_type_features(self, product_id, obj_features):
        if product_id == obj_features.product_line_id.id:
            return self._type_payment(obj_features)
        return []
    def _locale_date(self):
        locale.setlocale( locale.LC_TIME, 'es_MX.UTF-8' )
        return time.strftime('%B %Y')

report_sxw.report_sxw('report.account.analytic.account.report','account.analytic.account','addons/account_analytic_analysis_rent/report/account_analytic_analysis_report.rml',
    parser=account_analytic_account_report, header=False)
