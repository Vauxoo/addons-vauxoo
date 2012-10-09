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
        'not_acc_rec': self.not_acc_rec,
        })
    
    def not_acc_rec(self, company_id):
        partner_obj=self.pool.get('res.partner')
        property_obj = self.pool.get('ir.property')
        list_partners=partner_obj.search(self.cr, self.uid,[])
        lista=[]
        result=[]
        for partner_id in list_partners:
            rec_pro_id = property_obj.search(self.cr,self.uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
            if not rec_pro_id:
                lista.append(partner_id)
        for id_no_acc in lista:
            res={}
            print 'id_no_acc',id_no_acc
            partner=partner_obj.browse(self.cr,self.uid,id_no_acc)
            name=partner.name
            print 'name',name
            ref=partner.ref
            print 'ref',ref
            res['partner_id'] = id_no_acc or ''
            res['partner_name'] = name or ''
            res['partner_ref'] = ref or ''
            result.append(res)
        print 'res',result
        return result
        
report_sxw.report_sxw('report.partner.report','res.partner','modules_sys/query_partner/report/query_report.rml',parser=query_report,header=False)
