# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
import time
from osv import osv, fields

class wizard_account(osv.osv_memory):
    _name='wizard.account'
    _columns={
        'filter' : fields.selection([('filter_no','No Filtros'),('filter_date','Fecha'),('filter_period','Periodo')], 'Filtrar por', required=True),
        'partner' : fields.boolean('Group by Partner'),
        'show' : fields.boolean('Show All Accounts'),
        'period_from' : fields.many2one('account.period', 'Periodo Inicial'),
        'period_to' : fields.many2one('account.period', 'Periodo Final'),
        'date_ini' : fields.date('Fecha Inicial'),
        'date_fin' : fields.date('Fecha Final'),
        'nivel' : fields.integer('Nivel', required=True),
        'type_show' : fields.selection([('all','Con Valores en 0.0'),('only_for','initial, debit, credit <> 0.0')], 'Filtro'),
        'account_ids': fields.many2many('account.account', 'account_account_balanza_rel', 'balanza_id', 'account_id', 'Accounts'),
    }

    _defaults={
        'nivel' : 1,
        'filter' : lambda *a : 'filter_no'
    }

    def onchange_filter(self, cr, uid, ids, filter=False, context=None):
        res = {}
        if filter:
            res['value'] = {'period_from': False ,'period_to': False ,'date_ini': False ,'date_fin': False}
        return res

    def calculation(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])
        data = {
            'uid': uid,
            'ids': context.get('active_ids',[]),
            'model': 'wizard.account',
            'form': form,
            'context':context,
        }

        return {'type': 'ir.actions.report.xml', 'report_name': 'reportes.btree.report', 'datas': data, 'uid': uid}

wizard_account()
