#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import netsvc
import decimal_precision as dp
from DateTime import DateTime
import time


class ledger_report(osv.osv_memory):

    
    _name = 'ledger.report'
    _columns = {
        'partner_ids':fields.many2many('res.partner','partner_rel','partner1','partner2','Partners',help="Select the Partner"),
        'fiscalyear_id':fields.many2one('account.fiscalyear','Fiscal Year',help="Fiscal Year "),
        'period_id':fields.many2one('account.period','Period',help="Period"),
        'company_id':fields.many2one('res.company','Company'),
        'type_filter':fields.selection([('date','Date'),('period','Period'),('none','None')],'Filter'),
        'date_begin':fields.date('Date Begin',help="Date to begin filter"),
        'date_end':fields.date('Date End',help="Date to end filter"),
        
        
        
    }
    
    def generate_report(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
            
        return True
ledger_report()

