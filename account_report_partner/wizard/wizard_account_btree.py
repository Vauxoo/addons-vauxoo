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
        'filter' : fields.selection([('filter_no','No Filtros'),('filter_date','Fecha'),('filter_period','Periodos')], 'Filtrar por', required=True),
        'partner' : fields.boolean('Group by Partner'),
        'period_from' : fields.many2one('account.period', 'Periodo Inicial', required=True),
        'period_to' : fields.many2one('account.period', 'Periodo Final', required=True),
        'date_ini' : fields.date('Fecha Inicial', required=True),
        'date_fin' : fields.date('Fecha Final', required=True),
        'nivel' : fields.integer('Nivel', required=True),
        'account_ids': fields.many2many('account.account', 'account_account_balanza_rel', 'balanza_id', 'account_id', 'Accounts'),
    }

    _defaults={
        'nivel' : 1,
        'filter' : lambda *a : 'filter_no'
    }

    def calculation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form = self.read(cr,uid,ids,[])
        datas = {
            'ids': context.get('active_ids',[]),
            'model': 'wizard.account',
            'form': form,
            'uid': uid,
            'context':context,
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'reportes.btree.report',
            'datas': datas,
        }

wizard_account()
