# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from report import report_sxw
from osv import osv

class query_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context=None):
        super(query_report, self).__init__(cr,uid,name,context)
        self.localcontext.update({
        'not_acc_rec': self._not_acc_rec,
        })
    
    def _not_acc_rec(self, o):
        
        print 'res',o
        
        return o
report_sxw.report_sxw('report.partner.report','res.partner','modules_sys/query_partner/report/query_report.rml',parser=query_report,header=False)
