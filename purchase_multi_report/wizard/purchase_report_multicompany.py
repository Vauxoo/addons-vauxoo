# coding: utf-8
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#                Miguel Delgado          <miguel@openerp.com.ve>
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
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _

import base64
import openerp.workflow as workflow


class PrintPurchaseReport(osv.TransientModel):

    """OpenERP Wizard : print.purchase.report
    """
    _name = "print.purchase.report"

    def __get_company_object(self, cr, uid):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if not user.company_id:
            raise except_osv(_('ERROR !'), _(
                'There is no company configured for this user'))
        return user.company_id

    def _get_company(self, cr, uid, context=None):
        return self.__get_company_object(cr, uid).partner_id.name

    def _get_report(self, cr, uid, context=None):
        purch_order = self.pool.get("purchase.order").browse(
            cr, uid, context['active_ids'][0])
        if purch_order.state == 'approved':
            report = self.__get_company_object(cr, uid).purchase_report_id
        else:
            report = self.__get_company_object(cr, uid).purchase_request_id
        if not report:
            rep_id = self.pool.get("ir.actions.report.xml").search(
                cr, uid, [('model', '=', 'purchase.order'), ], order="id")[0]
            report = self.pool.get(
                "ir.actions.report.xml").browse(cr, uid, rep_id)

        service = netsvc.LocalService('report.' + report.report_name)
        (result, format) = service.create(cr, uid, context[
                                          'active_ids'], {'model': context['active_model']}, {})
        return base64.encodestring(result)

    def _get_report_name(self, cr, uid, context):
        purch_order = self.pool.get("purchase.order").browse(
            cr, uid, context['active_ids'][0])
        if purch_order.state == 'approved':
            report = self.__get_company_object(cr, uid).purchase_report_id
        else:
            report = self.__get_company_object(cr, uid).purchase_request_id
        if not report:
            rep_id = self.pool.get("ir.actions.report.xml").search(
                cr, uid, [('model', '=', 'purchase.order'), ], order="id")[0]
            report = self.pool.get(
                "ir.actions.report.xml").browse(cr, uid, rep_id)
        return report.report_name

    def print_report(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.report.xml', 'report_name': self._get_report_name(cr, uid, context), 'datas': {'ids': context['active_ids']}}

    _columns = {
        'company': fields.char('Company', 64, readonly=True, requied=True),
        'report_format': fields.binary("Report", readonly=True, required=True)
    }

    _defaults = {
        'company': _get_company,
        'report_format': _get_report,
    }
