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
    _columns = {
        'period': fields.many2one('account.period', 'Force period', help='Fiscal period to assign to the invoice. Keep empty to use the period of the current date.'),
        'fiscalyear_id' : fields.many2one('account.fiscalyear', 'Fiscal Year' ),
        'company_id' : fields.many2one('res.company', string='Company', ondelete='cascade', required = True ),
        'type': fields.selection( [
            ('ifrs','Two Columns'),
            ('ifrs_12', 'Twelve Columns')],
            string='Type', help='Number of columns to display', required=True ),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                        ('all', 'All Entries'),
                                        ], 'Target Moves'),
    }

    def _get_period(self, cr, uid, context={}):

        """ Return default account period value """

        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(cr, uid, context=context)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id

    def print_report(self, cr, uid, ids, context={}):
        datas = {'ids': context.get('active_ids', [])}
        wizard_ifrs = self.browse(cr, uid, ids, context=context)[0]

        datas['type'] = wizard_ifrs.type
        datas['ifrs_title'] = context['title']
        datas['company'] = wizard_ifrs.company_id.id

        if datas['type'] == 'ifrs_12':
            datas['period'] = 'All Periods'
        else:
            datas['period'] = wizard_ifrs.period.id or self._get_period(self, cr, uid)

        datas['fiscalyear'] = wizard_ifrs.fiscalyear_id.id or wizard_ifrs.period.fiscalyear_id.id

        return {
            'type': 'ir.actions.report.xml',
            'report_name': datas['type'],
            'datas' : datas
       }

ifrs_report_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
