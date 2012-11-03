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

from osv import osv
from osv import fields
import mx.DateTime

class account_period(osv.osv):
    _inherit='account.period'
    
    def _get_period_days(self, cr, uid, init_period, last_period, context = None):
        if context is None: context = {}
        date_start = self.browse(cr, uid, init_period, context = context).date_start
        date_stop = self.browse(cr, uid, last_period, context = context).date_stop
        
        date_start = mx.DateTime.strptime(date_start, '%Y-%m-%d')
        date_stop = mx.DateTime.strptime(date_stop, '%Y-%m-%d')
        return (date_stop - date_start).day + 1

    def previous(self, cr, uid, id, step=1, context=None):
        if context is None: context = {}
        period = self.pool.get('account.period').browse(cr,uid,id,context=context)
        
        #~ TODO: Take into account previous fiscalyear or just the fiscalyear of the period
        ids = self.search(cr, uid, [('date_stop','<=',period.date_start),('special','=',False)])
        if not ids:
            ids = self.search(cr, uid, [('date_stop','<=',period.date_start),('special','=',True)])
        if len(ids)>=step:
            return ids[-step]
        return False
account_period()

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"

    def _get_fy_period_ids(self, cr, uid, id, special=False, context=None):
        if context is None: context = {}
        res = self.pool.get('account.period').search(cr,uid,[special and ('fiscalyear_id','=',id) or ('fiscalyear_id','=',id),('special','=',special)],context=context)
        return res

    def _get_fy_periods(self, cr, uid, id, special=False, context=None):
        if context is None: context = {}
        return len(self._get_fy_period_ids(cr, uid, id, special=special, context=context))

    def _get_fy_month(self, cr, uid, id, period_id, special=False, context=None):
        if context is None: context = {}
        return self._get_fy_period_ids(cr, uid, id, special=special, context=context).index(period_id)+1

account_fiscalyear()
