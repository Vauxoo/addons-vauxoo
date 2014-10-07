#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time
import datetime
from mx.DateTime import *


class trial_cost(osv.TransientModel):
    logger = netsvc.Logger()
    _name = "trial.cost"
    _columns = {
        'date_start': fields.date('Start Date', required=True),
        'period_length': fields.integer('Period length (days)', required=True),
        'user_res_id': fields.many2one('res.users', 'Salesman'),
        'partner_res_id': fields.many2one('res.partner', 'Partner'),
        'cat_res_id': fields.many2one('product.category', 'Category'),
        'u_check': fields.boolean('Check salesman?'),
        'p_check': fields.boolean('Check partner?'),
        'c_check': fields.boolean('Check category?'),
    }

    _defaults = {
        'period_length': lambda *a: 30,
    }

    def action_print(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids[0])
        form = data['form']
        if not form['u_check'] and not form['p_check'] and not form['c_check']:
            raise osv.except_osv(_('User Error'), _(
                'You must check one box !'))
        res = {}
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise osv.except_osv(_('UserError'), _(
                'You must enter a period length that cannot be 0 or below !'))
        start = datetime.date.fromtimestamp(time.mktime(
            time.strptime(data['form']['date_start'], "%Y-%m-%d")))
        start = DateTime(int(start.year), int(start.month), int(start.day))

        for i in range(4)[::-1]:
            stop = start - RelativeDateTime(days=period_length)
            res[str(i)] = {
                'name': str((4 - (i + 1)) * period_length) +
                '-' + str((4 - i) * period_length),

                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d'),
            }
            start = stop - RelativeDateTime(days=1)

        data['form'].update(res)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'profit.trial.cost',
                'datas': data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
