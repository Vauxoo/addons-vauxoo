# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from report import report_sxw
from osv import osv
from tools.translate import _
from report import pyPdf

class sale_vauxoo_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_vauxoo_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'hello': self._hello,
            'get_addr': self._get_addr,
            'get_delay': self._get_delay,
            'get_rif': self._get_rif,
            
        })
    
    def _get_delay(self, obj):
        
        aux=[]
        
        for aux2 in obj.order_line:
            if aux2.delay > 0:
                aux.append(True)
            else:
                aux.append(False)
        print any(aux)
        return any(aux)
         
    def _get_rif(self,obj):
        rif = obj.user_id.company_id.partner_id.vat[2]+'-'+obj.user_id.company_id.partner_id.vat[3:]
        print 'rif',rif
        return rif 
        
    
    
    def _get_addr(self, idp=None,type_r=None):
        if not idp:
            return []
        print type_r
        addr_obj = self.pool.get('res.partner.address')
        res = ''
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp),('type','=',type_r)])
        addr_inv={}
        lista=""

        if addr_ids: 
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            lista=(hasattr(addr,'street') and addr.street and ('%s'%(addr.street)) or '')+(hasattr(addr,'street2') and addr.street2 and (', %s'%(addr.street2)) or '')+(hasattr(addr,'zipcode_id') and addr.zipcode_id and (',C.P: %s'%(addr.zipcode_id.name)) or '')+(hasattr(addr,'municipality_id') and addr.municipality_id and (', %s'%(addr.municipality_id.name)) or '')+(hasattr(addr,'parish_id') and addr.parish_id and (', %s'%(addr.parish_id.name)) or '')+(hasattr(addr,'city_id') and addr.city_id and (', %s'%(addr.city_id.name)) or '')+(addr.state_id and (', %s'%(hasattr(addr,'state_id') and addr.state_id.name)) or '')+(hasattr(addr,'country_id') and addr.country_id and (', %s'%(addr.country_id.name)) or '')+(hasattr(addr,'phone') and addr.phone and (',TELF.: %s'%(addr.phone)) or '') + (hasattr(addr,'fax') and  addr.fax and (',FAX: %s'%(addr.fax)) or '') +(hasattr(addr,'mobile') and addr.mobile and (',CEL.: %s'%(addr.mobile)) or '') 
        if lista:
            respuesta=lista
        else:
            respuesta=res
        return respuesta     
    
    
    def _hello(self,p):
        print "estoy en hello"
        return "Hello World %s"
report_sxw.report_sxw(
'report.sale_order_vauxoo',
'sale.order',
'addons/sale_order_report/report/vauxoo.rml',
parser=sale_vauxoo_report)
