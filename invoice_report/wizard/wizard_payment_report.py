# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: isaac (isaac@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
from osv import fields, osv
import time
#from tools.translate import _
#import pooler


class wizard_payment_report(osv.osv_memory):
    _name='wizard.payment.report'
    #Agregar domain al journal#domain=[('type','=','bank'
    _columns={
        'date_start': fields.date('Date start', required=True),
        'date_end': fields.date('Date end', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        #~ 'filter_type': fields.selection([('date', 'Date'),('period', 'Period')],'Filter Type', required=True),

        #~ 'period_start': fields.char('Period Start', size=64),
        #~ 'period_end': fields.char('Period End', size=64),
    }
    _defaults = {
        'date_start': time.strftime('%Y-%m-01'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        'currency_id': lambda self, cr, uid, ids, context=None: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id,
    }

    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]

        datas = {
            'ids': context.get('active_ids',[]),
            'model': 'wizard.payment.report',
            'form': data,
            'uid': uid,
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice.report.pagos',
            'datas': datas,
        }
wizard_payment_report()
