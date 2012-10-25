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

class account_period(osv.osv):
    _inherit='account.period'
    
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
