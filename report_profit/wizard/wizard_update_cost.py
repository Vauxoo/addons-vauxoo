# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import osv
import pooler
from tools.translate import _
import time
import datetime
from mx.DateTime import *


_transaction_form = '''<?xml version="1.0"?>
<form string="Select Date-Invoice">
    <separator string="Filters" colspan="4"/>
    <field name="state" required="True"/>
    <newline/>
    <group attrs="{'invisible':[('state','=','none')]}" colspan="4">
        <group attrs="{'invisible':[('state','!=','bydate')]}" colspan="4">
            <separator string="Date Filter" colspan="4"/>
            <field name="date_start" attrs="{'required':[('state','=','bydate')]}"/>
            <field name="date_end" attrs="{'required':[('state','=','bydate')]}"/>
        </group>
        <group attrs="{'invisible':[('state','!=','byinvoice')]}" colspan="4">
            <separator string="Filter by Invoice" colspan="4"/>
            <field name="invoice_id" colspan="4" nolabel="1"  attrs="{'required':[('state','=','byinvoice')]}"/>
        </group>
        <group attrs="{'invisible':[('state','in',['bydate', 'byinvoice'])]}" colspan="4">
            <separator string="Filter on Invoices" colspan="4"/>
            <field name="invoice_ids" colspan="4" nolabel="1"/>
        </group>
    </group>

</form>'''

_transaction_fields = {
    'date_start': {'string':'Start Date','type':'date','required': False},
    'date_end': {'string':'End Date','type':'date','required': False},
    'state':{
        'string':"Date/Period Filter",
        'type':'selection',
        'selection':[('bydate','By Date'),('byinvoice','By Invoice'),('some','By Invoices'),('none','No Filter')],
        'default': lambda *a:'none'
    },
    'invoice_id': {
        'string':'Invoice', 'type': 'many2one', 'relation': 'account.invoice',
        'default': lambda *a:False,
        'help': 'Keep empty for all open fiscal year'
    },
    'invoice_ids': {'string': 'Invoices', 'type': 'many2many', 'relation': 'account.invoice', 'help': 'All periods if empty'},
}

def _data_save(self, cr, uid, data, context):
    form = data['form']
    pool = pooler.get_pool(cr.dbname)
    prod_obj = pool.get('product.product')
    line_inv_obj = pool.get('report.profit.invoice')
    inv_ids = []
    res = {}
    
    
    cost_obj = pool.get('costo.inicial')
    inv_obj = pool.get('account.invoice')
    if form['state']=='bydate':
        inv_ids = inv_obj.search(cr,uid,[('date_invoice','>=',form['date_start']), ('date_invoice','<=',form['date_end'])])

    if form['state']=='byinvoice':
        inv_ids.append(form['invoice_id'])

    if form['state']=='some':
        if form['invoice_ids'] and form['invoice_ids'][0]:
            inv_ids.extend(form['invoice_ids'][0][2])

    if form['state']=='none':
        inv_ids = inv_obj.search(cr,uid,[])


    if inv_ids:
        inv_obj.button_reset_cost(cr, uid, inv_ids, context)

    il_ids = line_inv_obj.search(cr,uid,[])

    if il_ids:
        cr.execute('SELECT DISTINCT product_id FROM report_profit_invoice WHERE id in ('+','.join(map(str,il_ids))+')')
        prd_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
        for p_id in prd_ids:
            res[p_id] = []

        for line in line_inv_obj.browse(cr, uid, il_ids):
            dct = {}
            lst_tmp = []
            elem = False
            cost_ids = cost_obj.search(cr,uid,[('default_code','=',line.product_id.default_code)])
            if cost_ids:
                if len(cost_ids)==1:
                    elem=cost_ids[0]
                else:
                    raise wizard.except_wizard('Error','Codigo duplicado en csv importado')

            dct={
                'fecha': line.name,
                'costo': line.acc_cost,
                'cant': line.quantity,
                'tipo': line.invoice_id.type,
                'fact': line.invoice_id.id,
                'comp': line.move_id.id,
                'prod': line.product_id.id,
                'linea': line.line_id.id,
                'exist': line.stock,                
                'elem': elem
            }

            lst_tmp = res[line.product_id.id]
            lst_tmp.append(dct)
            res[line.product_id.id] = lst_tmp
               


    for pd_id in res.keys():
        dct = {}
        lst_tmp = []
        startf = datetime.date.fromtimestamp(time.mktime(time.strptime(time.strftime('%Y-%m-%d'),"%Y-%m-%d")))
        start = DateTime(int(startf.year),1,1)
        d1 = start.strftime('%Y-%m-%d')
        if res[pd_id] and res[pd_id][0]['elem']:
            c_ini = cost_obj.browse(cr, uid, res[pd_id][0]['elem'])
            dct={
                'fecha': d1,
                'costo': float(c_ini.standard_price.replace(',','')) or 0.0,
                'cant': float(c_ini.product_qty.replace(',','')) or 0.0,
                'tipo': u'cos_ini'
            }
            lst_tmp = res[pd_id]
            lst_tmp.append(dct)
            res[pd_id] = lst_tmp


    print 'ressssss: ',res            
    return {}

class wiz_update_cost(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Update')]}
        },
        'change': {
            'actions': [],
            'result': {'type': 'action', 'action':_data_save, 'state':'end'}
        }
    }
wiz_update_cost('account.update.cost')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

