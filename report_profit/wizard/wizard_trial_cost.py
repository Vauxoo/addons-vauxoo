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
<form string="Last Cost Price Sum">
    <separator string="Sum By?" colspan="4"/>
    <field name="date_start" />
    <field name="period_length"/>
    <newline/>
    <group col="4" colspan="2">
    <group col="4" colspan="2">
        <field name="u_check" />
        <field name="user_res_id" nolabel="1" attrs="{'readonly':[('u_check','!=',True)]}"/>
        <field name="u_sel" nolabel="1" attrs="{'readonly':[('u_check','!=',True)]}"/>
        <field name="p_check" />
        <field name="partner_res_id" nolabel="1" attrs="{'readonly':[('p_check','!=',True)]}"/>
        <field name="p_sel" nolabel="1" attrs="{'readonly':[('p_check','!=',True)]}"/>
        <field name="c_check" />
        <field name="cat_res_id" nolabel="1" attrs="{'readonly':[('c_check','!=',True)]}"/>
        <field name="c_sel" nolabel="1" attrs="{'readonly':[('c_check','!=',True)]}"/>
    </group>

    </group>  
</form>'''

_transaction_fields = {
    'period_length': {'string': 'Period length (days)', 'type': 'integer', 'required': True, 'default': lambda *a:30},
    'date_start': {'string':'Start Date','type':'date','required': True},
    'user_res_id': {'string':'Salesman', 'type':'many2one', 'relation': 'res.users','required':False},
    'partner_res_id': {'string':'Partner', 'type':'many2one', 'relation': 'res.partner','required':False},
    'cat_res_id': {'string':'Category', 'type':'many2one', 'relation': 'product.category','required':False},
    'u_check': {'string':'Check salesman?', 'type':'boolean'},
    'p_check': {'string':'Check partner?', 'type':'boolean'},
    'c_check': {'string':'Check category?', 'type':'boolean'},
    'u_sel':{
        'string':"Sequence",
        'type':'selection',
        'selection':[('one','1'),('two','2'),('three','3'),('none','No Filter')],
        'default': lambda *a:'none'
    },
    'p_sel':{
        'string':"Sequence",
        'type':'selection',
        'selection':[('one','1'),('two','2'),('three','3'),('none','No Filter')],
        'default': lambda *a:'none'
    },
    'c_sel':{
        'string':"Sequence",
        'type':'selection',
        'selection':[('one','1'),('two','2'),('three','3'),('none','No Filter')],
        'default': lambda *a:'none'
    },


}

def _data_save(self, cr, uid, data, context):
    form = data['form']
    if not form['u_check']  and not form['p_check'] and not form['c_check']:
        raise wizard.except_wizard(_('User Error'), _('You have to check one box !'))    
    res = {}
    period_length = data['form']['period_length']
    if period_length<=0:
        raise wizard.except_wizard(_('UserError'), _('You must enter a period length that cannot be 0 or below !'))
    start = datetime.date.fromtimestamp(time.mktime(time.strptime(data['form']['date_start'],"%Y-%m-%d")))
    start = DateTime(int(start.year),int(start.month),int(start.day))

    for i in range(4)[::-1]:
        stop = start - RelativeDateTime(days=period_length)
        res[str(i)] = {
            'name' : str((4-(i+1))*period_length) + '-' + str((4-i)*period_length),
            
            'stop': start.strftime('%Y-%m-%d'),
            'start' : stop.strftime('%Y-%m-%d'),
            }
        start = stop - RelativeDateTime(days=1)

    return res

class wiz_trial_cost(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('print','Print Trial Profitability')]}
        },
        'print': {
            'actions': [_data_save],
            'result': {'type':'print', 'report':'profit.trial.cost', 'state':'end'},
        },

    }
wiz_trial_cost('profit.trial.cost')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

