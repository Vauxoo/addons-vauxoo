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
import pooler
import time
from osv import osv, fields

class wizard_account(osv.osv_memory):
    _name='wizard.account'
    _columns={
        'date_ini' : fields.date('Fecha Inicial', required=True),
        'date_fin' : fields.date('Fecha Final', required=True),
        'nivel' : fields.integer('Nivel', required=True),
        'account_ids': fields.many2many('account.account', 'account_account_balanza_rel', 'balanza_id', 'account_id', 'Accounts')
    }

    _defaults={
        'nivel' : 1
    }

    def calculation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form = self.read(cr,uid,ids,[])
        wizard_id=context.get('active_id',False)
        nivel = form and form[0]['nivel']
        date_ini = form and form[0]['date_ini'] or False
        date_fin = form and form[0]['date_fin'] or False
        account_ids = form and form[0]['account_ids'] or False
        context.update({'account_ids': account_ids})
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
