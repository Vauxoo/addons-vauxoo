# -*- encoding: utf-8 -*- #
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).                           #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)                         #
#    Planified by: Nhomar Hernandez (nhomar@vauxoo.com)                    #
#    Finance by: COMPANY NAME <EMAIL-COMPANY>                              #
#    Audited by: author NAME LASTNAME <email@vauxoo.com>                   #
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
from openerp.osv import fields, osv
from openerp.tools.translate import _

import base64
import openerp.netsvc as netsvc
import logging
_logger = logging.getLogger(__name__)

class invoice_report_per_journal(osv.TransientModel):
    """
    OpenERP Wizard: invoice.report.per.journal
    """
    _name = "invoice.report.per.journal"
 
    def get_journal_object(self, cr, uid, context=None):
        record_brw = self.pool.get(context['active_model']).browse(
                                cr, uid, context['active_ids'][0])
        if not record_brw.journal_id:
            raise except_osv(_('ERROR !'), _(
                'There is no journal configured for this invoice.'))
        return record_brw.journal_id

    def _get_journal(self, cr, uid, context=None):
        return self.get_journal_object(cr, uid, context=context).name
        
    def _prepare_service(self, cr, uid, report, context=None):
        service = netsvc.LocalService('report.' + report.report_name)
        (result, format) = service.create(cr, uid, context[
                    'active_ids'], {'model': context['active_model']}, {})
        return (result, format)

    def _get_report(self, cr, uid, context=None):
        report = self.get_journal_object(
                            cr, uid, context=context).invoice_report_id
        try:
            (result, format) = self._prepare_service(cr, uid, report, context=context)
        except:
            if report:
                _logger.warning("Error occurred in the report, the report set to the journal will be ignored.")
            rep_id = self.pool.get("ir.actions.report.xml").search(
                cr, uid, [('model', '=', 'account.invoice'),], order="id",
                        context=context)[0]
            report_ = self.pool.get(
                    "ir.actions.report.xml").browse(cr, uid, rep_id, context=context)
            (result, format) = self._prepare_service(cr, uid, report_, context=context)
        try:
            act_id = self.pool.get('ir.actions.act_window').search(cr, uid, [('name','=', report.name + ' txt')], context=context)[0]
            if act_id:
                act_brw = self.pool.get('ir.actions.act_window').browse(cr, uid, act_id, context=context)
                wiz_obj = self.pool.get(act_brw.res_model)
                wiz_id = wiz_obj.create(cr, uid, {}, context=context)
                wiz_brw = wiz_obj.browse(cr, uid, wiz_id, context=context)
                result = base64.decodestring(wiz_brw.fname_txt)
        except:
            if report:
                _logger.info("txt report not defined for the report assigned to journal.")
        return base64.encodestring(result)

    def _get_report_name(self, cr, uid, context=None):
        report = self.get_journal_object(cr, uid,
                                    context=context).invoice_report_id
        try:
            (result, format) = self._prepare_service(cr, uid, report, context=context)
        except:
            if report:
                _logger.warning("Error occurred in the report, the report set to the journal will be ignored.")
            rep_id = self.pool.get("ir.actions.report.xml").search(
                cr, uid, [('model', '=', 'account.invoice'),], order="id",
                        context=context)[0]
            report = self.pool.get(
                "ir.actions.report.xml").browse(cr, uid, rep_id, context=context)
        return report.report_name

    def print_invoice(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.report.xml',
            'report_name': self._get_report_name(cr, uid, context=context),
            'datas': {'ids': context['active_ids']}}

    _columns = {
        'journal': fields.char('Journal', 64, readonly=True, requied=True),
        'report_format': fields.binary("Report", readonly=True, required=True)
    }

    _defaults = {
        'journal': _get_journal,
        'report_format': _get_report,
    }
