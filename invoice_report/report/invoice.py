# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque gabriela@openerp.com.ve
#              Luis Escobar luis@vauxoo.com
#    Planified by: Maria Gabriela Quilarque gabriela@openerp.com.ve
#    Finance by: Vauxoo, C.A. http://www.vauxoo.com
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################

import time
from report import report_sxw

class invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_company_addr': self._get_company_addr,
            'get_fiscal_addr': self._get_fiscal_addr,
            'get_contact_addr': self._get_contact_addr,
            'get_tipo':self.get_tipo,
        })


    def _get_company_addr(self):
        company_obj = self.pool.get('res.company')
        company_ids = company_obj.search(self.cr,self.uid,[])
        company = company_obj.browse(self.cr, self.uid, company_ids[0])
        addr_com = self._get_partner_addr(company.partner_id.id)
        return addr_com


    #metodo que retorna la direccion fiscal si es de tipo invoice 
    def _get_fiscal_addr(self, idp=None):
        if not idp:
            return []
        addr_obj = self.pool.get('res.partner.address')
        res = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        addr_inv={}
        lista=""

        if addr_ids: 
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            lista=(addr.street and ('%s, '%(addr.street)) or '')+' '+(addr.street2 and ('%s - '%(addr.street2)) or '')+' '+(addr.zipcode_id and ('C.P. %s - '%(addr.zipcode_id.name)) or '')+ ' '+(addr.municipality_id and ('%s - '%(addr.municipality_id.name)) or '')+ ' '+(addr.parish_id and ('%s - '%(addr.parish_id.name)) or '')+ ' '+(addr.city_id and ('%s - '%(addr.city_id.name)) or '')+ ' '+(addr.state_id and ('%s - '%(addr.state_id.name)) or '')+' '+(addr.country_id and ('%s '%(addr.country_id.name)) or '')+ '\n '+ (addr.phone and (' TELF.: %s '%(addr.phone)) or '') + (addr.fax and (' FAX: %s '%(addr.fax)) or '') +(addr.mobile and (' CEL.: %s '%(addr.mobile)) or '') + (addr.email and (' EMAIL: %s '%(addr.email)) or '') 

        if lista:
            respuesta=lista
        else:
            respuesta=res
        return respuesta 

    #metodo que retorna la direccion de contacto si es de tipo contact 
    def _get_contact_addr(self, idp=None):
        if not idp:
            return []
        addr_obj = self.pool.get('res.partner.address')
        res = ''
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','contact')])
        addr_inv={}
        lista=""

        if addr_ids: 
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            if addr.name:
                lista=('CONTACTO: %s, '%addr.name) + (addr.street and ('%s, '%(addr.street)) or '')+' '+(addr.street2 and ('%s - '%(addr.street2)) or '')+' '+(addr.zipcode_id and ('C.P. %s - '%(addr.zipcode_id.name)) or '')+ ' '+(addr.municipality_id and ('%s - '%(addr.municipality_id.name)) or '')+ ' '+(addr.parish_id and ('%s - '%(addr.parish_id.name)) or '')+ ' '+(addr.city_id and ('%s - '%(addr.city_id.name)) or '')+ ' '+(addr.state_id and ('%s - '%(addr.state_id.name)) or '')+' '+(addr.country_id and ('%s '%(addr.country_id.name)) or '')+ '\n '+ (addr.phone and (' TELF.: %s '%(addr.phone)) or '') + (addr.fax and (' FAX: %s '%(addr.fax)) or '') +(addr.mobile and (' CEL.: %s '%(addr.mobile)) or '') + (addr.email and (' EMAIL: %s '%(addr.email)) or '') 

        if lista:
            respuesta=lista
        else:
            respuesta=res
        return respuesta 


    def get_tipo(self, idp=None):
        if not idp:
            return []
        print idp
        res=" "
        if idp == 'in_invoice' or idp == 'in_refund':
            res="Compra"
        elif idp == 'out_invoice' or idp == 'out_refund':
            res="Venta"     
            
        return res 


report_sxw.report_sxw( #nuevo
    'report.account.invoice_vauxoo',
    'account.invoice',
    'addons/invoice_report/report/invoice.rml',
    parser=invoice_report,
    header = False 
)

