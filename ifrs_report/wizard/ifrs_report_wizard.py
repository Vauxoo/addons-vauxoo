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

from osv import fields, osv
from tools.translate import _
import netsvc


class ifrs_report_wizard(osv.osv_memory):

    """ Wizard que permite al usuario elegir que periodo quiere imprimir del año fiscal """

    _name = 'ifrs.report.wizard'
    _description = 'IFRS Report'

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        context = context or {}
        context['company_id'] = company_id
        res = {'value': {}}

        if not company_id:
            return res

        cur_id = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context).currency_id.id
        fy_id = self.pool.get('account.fiscalyear').find(
            cr, uid, context=context)

        res['value'].update({'fiscalyear_id': fy_id})
        res['value'].update({'currency_id': cur_id})
        return res

    _columns = {
        'period': fields.many2one('account.period', 'Force period', help='Fiscal period to assign to the invoice. Keep empty to use the period of the current date.'),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Fiscal Year'),
        'company_id': fields.many2one('res.company', string='Company', ondelete='cascade', required=True, help='Company name'),
        'currency_id': fields.many2one('res.currency', 'Currency', help="Currency at which this report will be expressed. If not selected will be used the one set in the company"),
        'exchange_date': fields.date('Exchange Date', help='Date of change that will be printed in the report, with respect to the currency of the company'),
        'report_type': fields.selection([
            ('all', 'All Fiscalyear'),
            ('per', 'Force Period')],
            string='Type', required=True, help='Indicates if the report it will be printed for the entire fiscal year, or for a particular period'),
        'columns': fields.selection([
            ('ifrs', 'Two Columns'),
            ('webkitaccount.ifrs_12', 'Twelve Columns'),
            #('ifrs_12_partner_detail', 'With Partner Detail')
        ],
            string='Number of Columns',
            help='Number of columns that will be printed in the report:'
            " -Two Colums(02),-Twelve Columns(12)"),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                        ('all', 'All Entries'),
                                         ], 'Target Moves', help='Print All Accounting Entries or just Posted Accounting Entries'),
        'report_format' : fields.selection([
            ('pdf', 'PDF'),
            ('spreadsheet', 'Spreadsheet')], 'Report Format')
    }

    _defaults = {
        'report_type': 'all',
        'target_move': 'posted',
        'company_id': lambda self, cr, uid, c: self.pool.get('ifrs.ifrs').browse(cr, uid, c.get('active_id')).company_id.id,
        'fiscalyear_id': lambda self, cr, uid, c: self.pool.get('ifrs.ifrs').browse(cr, uid, c.get('active_id')).fiscalyear_id.id,
        'exchange_date': fields.date.today,
        'columns': 'ifrs',
        'report_format' : 'pdf'
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(ifrs_report_wizard, self).default_get(
            cr, uid, fields, context=context)
        # res.update({'uid_country':
        # self._get_country_code(cr,uid,context=context)})
        return res

    def _get_period(self, cr, uid, context={}):

        """ Return the current period id """

        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(
            cr, uid, time.strftime('%Y-%m-%d'), context=context)
        period_id = ids[0]
        return period_id

    def _get_fiscalyear(self, cr, uid, context={}, period_id=False):

        """ Return fiscalyear id for the period_id given.
            If period_id is nor given then return the current fiscalyear """

        if period_id:
            period_obj = self.pool.get(
                'account.period').browse(cr, uid, period_id)
            fiscalyear_id = period_obj.fiscalyear_id.id
        else:
            fiscalyear_obj = self.pool.get('account.fiscalyear')
            ids = fiscalyear_obj.find(cr, uid, time.strftime(
                '%Y-%m-%d'), context=context)
            fiscalyear_id = ids
        return fiscalyear_id

    def print_report(self, cr, uid, ids, context={}):
        datas = {'ids': context.get('active_ids', [])}
        wizard_ifrs = self.browse(cr, uid, ids, context=context)[0]
        datas['report_type'] = str(wizard_ifrs.report_type)
        datas['company'] = wizard_ifrs.company_id.id
        datas['columns'] = str(wizard_ifrs.columns)
        datas['target_move'] = wizard_ifrs.target_move
        datas['exchange_date'] = wizard_ifrs.exchange_date
        datas['currency_wizard'] = wizard_ifrs.currency_id.id
        datas['currency_wizard_name'] = wizard_ifrs.currency_id.name

        if datas['report_type'] == 'all':
            datas['fiscalyear'] = wizard_ifrs.fiscalyear_id.id or self._get_fiscalyear(
                cr, uid, context=context)
            datas['period'] = False
        else:
            datas['columns'] = 'ifrs'
            datas['period'] = wizard_ifrs.period.id or self._get_period(
                cr, uid, context=context)
            datas['fiscalyear'] = self._get_fiscalyear(
                cr, uid, context=context, period_id=datas['period'])
        if str(wizard_ifrs.columns) == 'webkitaccount.ifrs_12' and wizard_ifrs.report_format == 'spreadsheet':
            datas['columns'] = 'webkitaccount.ifrs_12_html'
        if str(wizard_ifrs.columns) == 'ifrs' and wizard_ifrs.report_format == 'spreadsheet':
            datas['columns'] = 'ifrs_report_html'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': datas['columns'],
            'datas': datas
        }

ifrs_report_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
