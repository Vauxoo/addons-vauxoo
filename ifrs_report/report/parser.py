#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Katherine Zaoral <katherine.zaoral@vauxoo.com>
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>           
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################



#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Katherine Zaoral <katherine.zaoral@vauxoo.com>
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>           
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


import time
from report import report_sxw
import mx.DateTime

class ifrs_report(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(ifrs_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
		'time': time,
		'get_lines': self._get_lines,
		'get_hour': self._get_hour,
		'get_time': self._get_time,
		#~ 'lines': self.lines,
		})
		self.cr = cr
		self.context = context
		self.uid = uid

	def _get_lines(self, ifrs_brws):
		res = {}
		#~ print ifrs_brws
		for ifrs_line in ifrs_brws.ifrs_lines_ids:
			p = ifrs_line.id
			
			acum = 0.0		
			if ifrs_line.type == 'abtract':
				pass
			elif ifrs_line.type == 'detail':
				pass
				#~ for a in ifrs_line.cons_ids:
					#~ acum += a.balance
					#~ print a 
			elif ifrs_line.type == 'total':
				pass
				#~ for c in brw.total_ids:
					#~ acum += self._get_sum( cr, uid, c.id, context = context )
			
			#~ print ifrs_line.type
			#~ print acum
			
			res[p] = {'name':ifrs_line.name,'amount':ifrs_line.amount}
			#~ print ifrs_line.name
		return (res,)

	def _get_hour(self,float_hour,format='hh:mm:ss'):
		seconds=int(float_hour*3600)
		hours = seconds / 3600
		seconds -= 3600*hours
		minutes = seconds / 60
		seconds -= 60*minutes
		return format=='hh:mm:ss' and "%02d:%02d:%02d" % (hours, minutes, seconds)  or "%02d:%02d" % (hours, minutes+round(seconds/60.0))

	def _get_time(self, strtime = time.strftime('%Y-%m-%d %H:%M:%S')):
		t = time.strptime(strtime,'%Y-%m-%d %H:%M:%S')
		t = time.mktime(t)

		return time.strftime('%Y-%m-%d', time.gmtime(t))

	#~ def lines(self, form, ids=[], done=None):
		#~ def _process_child(accounts, disp_acc, parent):
			#~ account_rec = [acct for acct in accounts if acct['id']==parent][0]
			#~ currency_obj = self.pool.get('res.currency')
			#~ acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
			#~ 
			#~ currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
			#~ res = {
				#~ 'id': account_rec['id'],
				#~ 'type': account_rec['type'],
				#~ 'code': account_rec['code'],
				#~ 'name': account_rec['name'],
				#~ 'level': account_rec['level'],
				#~ 'debit': account_rec['debit'],
				#~ 'credit': account_rec['credit'],
				#~ 'balance': account_rec['balance'],
				#~ 'parent_id': account_rec['parent_id'],
				#~ 'bal_type': '',
			#~ }
			#~ self.sum_debit += account_rec['debit']
			#~ self.sum_credit += account_rec['credit']
			#~ if disp_acc == 'movement':
				#~ if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
					#~ self.result_acc.append(res)
			#~ elif disp_acc == 'not_zero':
				#~ if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
					#~ self.result_acc.append(res)
			#~ else:
				#~ self.result_acc.append(res)
			#~ if account_rec['child_id']:
				#~ for child in account_rec['child_id']:
					#~ _process_child(accounts,disp_acc,child)
#~ 
        #~ obj_account = self.pool.get('account.account')
        #~ if not ids:
            #~ ids = self.ids
        #~ if not ids:
            #~ return []
        #~ if not done:
            #~ done={}
#~ 
        #~ ctx = self.context.copy()
#~ 
        #~ ctx['fiscalyear'] = form['fiscalyear_id']
        #~ if form['filter'] == 'filter_period':
            #~ ctx['period_from'] = form['period_from']
            #~ ctx['period_to'] = form['period_to']
        #~ elif form['filter'] == 'filter_date':
            #~ ctx['date_from'] = form['date_from']
            #~ ctx['date_to'] =  form['date_to']
        #~ ctx['state'] = form['target_move']
        #~ parents = ids
        #~ child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        #~ if child_ids:
            #~ ids = child_ids
        #~ accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
#~ 
        #~ for parent in parents:
                #~ if parent in done:
                    #~ continue
                #~ done[parent] = 1
                #~ _process_child(accounts,form['display_account'],parent)
        #~ return self.result_acc	

    #~ def _get_lines(self, ptw_brws):
        #~ res = {}
        #~ 
        #~ for ptw in ptw_brws:
            #~ 
            #~ prt, p = ptw.partner_id  or False, ptw.partner_id and ptw.partner_id.id or False
            #~ pjt, j = ptw.project_id  or False, ptw.project_id and ptw.project_id.id or False
            #~ iss, i = ptw.issue_id  or False, ptw.issue_id and ptw.issue_id.id or False
            #~ 
                        #~ 
            #~ Llenar los partners en el diccionario
            #~ if res.get(p):
                #~ res[p]['t']+= ptw.hours
            #~ else:
                #~ res[p] = {'o':prt,'d':{}, 't':ptw.hours}
#~ 
            #~ Llenar los proyectos en el diccionario
            #~ if not res[p]['d'].get(j):
                #~ res[p]['d'][j] = {'o':pjt,'d':{}}
#~ 
            #~ Llenar las incidencias en el diccionario
            #~ if res[p]['d'][j]['d'].get(i):
                #~ res[p]['d'][j]['d'][i]['d'].append(ptw)
            #~ else:
                #~ res[p]['d'][j]['d'][i] = {'o':iss,'d':[ptw]}
        #~ return (res,)

report_sxw.report_sxw(
    'report.ifrs',
    'ifrs.ifrs',
    'ifrs_report/report/ifrs_cash_flow_indirect.rml',
    parser=ifrs_report,
    header = False 
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
