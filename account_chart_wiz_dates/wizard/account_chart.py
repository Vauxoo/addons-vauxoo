# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import osv, fields
import time


class account_chart(osv.TransientModel):
    _inherit = "account.chart"

    _columns = {
        'filter': fields.selection([('filter_no', 'Unfiltered'),
                                    ('periods', 'Periods'), ('dates', 'Dates')
                                    ], 'Filter',),
        'initial_date': fields.date('Initial date',),
        'end_date': fields.date('End date',),
    }

    _defaults = {
        'filter': 'filter_no',
    }

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                            val_filter=False, context=None):
        res = {}
        if val_filter == 'periods':
            res = super(account_chart, self).onchange_fiscalyear(
                cr, uid, ids, fiscalyear_id=fiscalyear_id, context=context)
        return res

    def onchange_val_filter(self, cr, uid, ids, val_filter=False,
                            fiscalyear_id=False, context=None):
        res = {}
        if val_filter == 'dates':
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'initial_date': time.strftime('%Y-01-01'),
                'end_date': time.strftime('%Y-%m-%d')}
        elif val_filter == 'periods':
            res = super(account_chart, self).onchange_fiscalyear(
                cr, uid, ids, fiscalyear_id=fiscalyear_id, context=context)
            res['value']['initial_date'] = False
            res['value']['end_date'] = False
        elif val_filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to':
                            False, 'initial_date': False, 'end_date': False}
        return res

    def account_chart_open_window(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        filter_val = data.get('filter', False) and data['filter'] or False
        result = super(account_chart, self).account_chart_open_window(
            cr, uid, ids, context=context)
        if filter_val == 'dates':
            # date_from=str({'date_from':data.get('initial_date', False)})
            # date_to=str({'date_to':data.get('end_date', False)})
            #~ result_get=result.get('context')
            context_dict = eval(result['context'])
            context_dict.update({
                'date_from': data.get('initial_date', False),
                'date_to': data.get('end_date', False),
            })
            result['context'] = str(context_dict)
            # result['context']='{'+result_get[1:-1]+', '+date_from[1:-1]+',
            # '+date_to[1:-1]+'}'
        return result
