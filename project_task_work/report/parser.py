#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>           
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
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

class project_task_work_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(project_task_work_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
        })

    def _get_lines(self, ptw_brws):
        res = {}
        
        for ptw in ptw_brws:
            
            prt, p = ptw.partner_id  or False, ptw.partner_id and ptw.partner_id.id or False
            pjt, j = ptw.project_id  or False, ptw.project_id and ptw.project_id.id or False
            iss, i = ptw.issue_id  or False, ptw.issue_id and ptw.issue_id.id or False
            
                        
            #~ Llenar los partners en el diccionario
            if not res.get(p):
                res[p] = {'o':prt,'d':{}}

            #~ Llenar los proyectos en el diccionario
            if not res[p]['d'].get(j):
                res[p]['d'][j] = {'o':pjt,'d':{}}

            #~ Llenar las incidencias en el diccionario
            if res[p]['d'][j]['d'].get(i):
                res[p]['d'][j]['d'][i]['d'].append(ptw)
            else:
                res[p]['d'][j]['d'][i] = {'o':iss,'d':[ptw]}
        return (res,)
        
    def _get_aml(self,ids):
        aml_obj= self.pool.get('account.move.line')
        res = 0.0
        if not ids:
            return res
        aml_gen = (aml_brw.debit and aml_brw.debit or aml_brw.credit * -1 for aml_brw in aml_obj.browse(self.cr,self.uid,ids))
        for i in aml_gen:
            res+=i
        return res

    def _get_total_by_comercial(self, rp_brws):
        ixp_gen = self._get_invoice_by_partner(rp_brws)
        total=0.0
        usr_dict = {}
        for ixp in ixp_gen:
            usr_id = ixp['rp_brw'].user_id and ixp['rp_brw'].user_id.id or False

            if usr_dict.get(usr_id):
                usr_dict[usr_id]['total'] += ixp['due_total']
            else:
                usr_dict[usr_id] = {
                    'usr_brw': ixp['rp_brw'].user_id,
                    'total' : ixp['due_total']
                }
            total+=ixp['due_total']
        if not total: return []
        return [{'total':total,'vendor':(usr_dict[i] for i in usr_dict)}]

    def _get_invoice_by_partner(self,rp_brws):
        res= {}
        rp_obj = self.pool.get('res.partner')
        inv_obj = self.pool.get('account.invoice')
        mun_obj  = self.pool.get('account.wh.munici.line')
        for rp_brw in rp_brws:
            inv_ids = inv_obj.search(self.cr,self.uid,[('partner_id','=',rp_brw.id),
                        ('type','=','out_invoice'),('residual','!=',0),('state','not in',('cancel','draft'))])
            if not inv_ids:
                continue
            res[rp_brw.id]={
                'rp_brw':rp_brw,
                'inv_ids':[],
                'inv_total':0.0,
                'wh_vat':0.0,
                'wh_islr':0.0,
                'wh_muni':0.0,
                'credit_note':0.0,
                'pay_left_total':0.0,
                'pay_total':0.0,
                'due_total':0.0,
                }
            for inv_brw in inv_obj.browse(self.cr,self.uid,inv_ids):
                
                pay_ids = [aml.id for aml in inv_brw.payment_ids]
                #~ VAT
                wh_lines = inv_brw.wh_iva_id and inv_brw.wh_iva_id.wh_lines and [line for line in inv_brw.wh_iva_id.wh_lines if inv_brw.id == line.invoice_id.id and line.move_id] or []
                pay_vat_ids = wh_lines and [aml.id for aml in line.move_id.line_id for line in wh_lines if aml.account_id.id == inv_brw.account_id.id] or []
                #~ ISLR
                wh_lines = inv_brw.islr_wh_doc_id and inv_brw.islr_wh_doc_id.concept_ids and [line for line in inv_brw.islr_wh_doc_id.concept_ids if line.move_id] or []
                pay_islr_ids = wh_lines and [aml.id for aml in line.move_id.line_id for line in wh_lines if aml.account_id.id == inv_brw.account_id.id] or []
               #~  MUNI
                wh_lines = mun_obj.search(self.cr,self.uid,[('invoice_id','=',inv_brw.id),('move_id','!=',False)])
                pay_muni_ids = wh_lines and [aml.id for aml in line.move_id.line_id for line in mun_obj.browse(self.cr,self.uid,wh_lines) if aml.account_id.id == inv_brw.account_id.id] or []
                #~  TODO: SRC
                
                #~ N/C
                refund_ids = inv_obj.search(self.cr,self.uid,[('parent_id','=',inv_brw.id),('type','=','out_refund'),('state','not in',('draft','cancel')),('move_id','!=',False)])
                refund_brws = refund_ids and inv_obj.browse(self.cr,self.uid,refund_ids) or []
                aml_gen = (refund_brw.move_id.line_id for refund_brw in refund_brws)
                pay_refund_ids = []
                for aml_brws in aml_gen:
                    pay_refund_ids += [aml.id for aml in aml_brws if aml.account_id.id == inv_brw.account_id.id]
                
                #~  TODO: N/D
                #~  ACUMULACION DE LOS NOPAGOS, OBTENCION DEL PAGO
                pay_left_ids = list(set(pay_ids).difference(\
                                        pay_vat_ids     +\
                                        pay_islr_ids    +\
                                        pay_muni_ids    +\
                                        pay_refund_ids  ))
                wh_vat = self._get_aml(pay_vat_ids)
                wh_islr = self._get_aml(pay_islr_ids)
                wh_muni = self._get_aml(pay_muni_ids)
                wh_src = self._get_aml([])
                debit_note = self._get_aml([])
                credit_note = self._get_aml(pay_refund_ids)
                payment_left = self._get_aml(pay_left_ids)
                payment = wh_vat + wh_islr + wh_muni + wh_src + debit_note + credit_note + payment_left
                residual = inv_brw.amount_total + payment
                date_due = mx.DateTime.strptime(inv_brw.date_due or inv_brw.date_invoice, '%Y-%m-%d')
                today = mx.DateTime.now()
                due_days = (today - date_due).day
                
                #~ TODO: Si se incluye un reporte de revisiones
                #~ no se eliminara la factura
                #~ si la factura no tiene saldo entonces
                #~ no incluirla en el reporte
                if not residual: continue
                
                res[rp_brw.id]['inv_ids'].append({
                    'inv_brw':inv_brw,
                    'wh_vat':wh_vat,
                    'wh_islr':wh_islr,
                    'wh_muni':wh_muni,
                    'wh_src':wh_src,
                    'debit_note':debit_note,
                    'credit_note':credit_note,
                    'refund_brws':refund_brws,
                    'payment':payment,
                    'payment_left':payment_left,
                    'residual':residual,
                    'due_days':due_days
                })
                res[rp_brw.id]['inv_total']+=inv_brw.amount_total
                res[rp_brw.id]['wh_vat']+=wh_vat
                res[rp_brw.id]['wh_islr']+=wh_islr
                res[rp_brw.id]['wh_muni']+=wh_muni
                res[rp_brw.id]['credit_note']+=credit_note
                res[rp_brw.id]['pay_left_total']+=payment_left
                res[rp_brw.id]['pay_total']+=payment
                res[rp_brw.id]['due_total']+=residual
            #~ TODO: Report donde no se elimine esta clave del diccionario
            #~ y se use para revisiones internas
            #~ Si no tiene saldo, sacarlo del reporte
            not res[rp_brw.id]['due_total'] and res.pop(rp_brw.id)
        
        #~ ordenando los registros en orden alfabetico
        #~ si llegaran a existir
        res2= []
        if res.keys():
            rp_ids = rp_obj.search(self.cr,self.uid,[('id','in',res.keys())],order='name asc')
            for rp_id in rp_ids:
                res2.append(res[rp_id])
        return res2

report_sxw.report_sxw(
    'report.project_task_work',
    'project.task.work',
    'addons/project_task_work/report/project_task_work.rml',
    parser=project_task_work_report,
    header = False 
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
