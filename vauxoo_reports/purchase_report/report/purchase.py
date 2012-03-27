#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Nhomar Hernandez          <nhomar@openerp.com.ve>
#    Planified by: Humberto Arocha
#    Finance by: Vauxoo, C.A. http://vauxoo.com
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

class purchase_vauxoo(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_vauxoo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_alicuota': self._get_alicuota,
            'get_footer_addr': self._get_footer_addr
                    })

    #metodo que retorna la direccion fiscal si es de tipo invoice o de tipo delivery
    def _get_partner_addr(self, idp=None):
        if not idp:
            return []
        addr_obj = self.pool.get('res.partner.address')
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        addr_inv={}
        lista=""
        if addr_ids: #si es de tipo invoice la direccion              
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            var=(addr.street2 and ('%s '%addr.street2.title()) or '')      +\
             (addr.zip and ('Codigo Postal: %s, '%addr.zip) or '')        +\
             (addr.state_id and ('%s, '%addr.state_id.name.title()) or '')+ \
             (addr.city and ('%s, '%addr.city.title()) or '')+ \
             (addr.country_id and ('%s '%addr.country_id.name.title()) or '')+ \
             (addr.phone and ('\nTelf:%s, '%addr.phone) or '')          +\
             (addr.mobile and ('Cel:%s, '%addr.mobile) or '')         +\
             (addr.fax and ('Fax:%s'%addr.fax) or '')
            
        if addr_ids:
            addr_inv['invoice'] = var
            lista= var
        if addr_inv:
            respuesta=lista
        else:
            respuesta=res
        return respuesta          
        
    #metodo que retorna la direccion fiscal si es de tipo invoice o de tipo delivery
    def _get_footer_addr(self, idp=None):
        res = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_obj = self.pool.get('res.partner.address')
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        addr_inv={}
        
        if addr_ids: #si es de tipo invoice la direccion
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            var =    \
            (addr.street and ('%s '%addr.street.title()) or '')    + \
            (addr.street2 and ('%s '%addr.street2.title()) or '')      +\
            (addr.zip and ('Codigo Postal: %s, '%addr.zip) or '')        +\
            (addr.city and ('%s, '%addr.city.title()) or '')+ \
            (addr.state_id and ('%s, '%addr.state_id.name.title()) or '')+ \
            (addr.country_id and ('%s, '%addr.country_id.name.title()) or '')+ \
            (addr.fax and ('Fax.: %s'%addr.fax) or '')+\
            (addr.email and (',Email.: %s'%addr.email) or '')+\
            (addr.partner_id.website and ('\n Puede conseguir mas informacion acerca de nosotros en: %s > Contacto > Contactenos '%addr.partner_id.website) or '')
            addr_inv['invoice'] = var
        if addr_inv.get('invoice',False):
            return addr_inv['invoice']
        return res   


    def _get_alicuota(self, line=None):
        if not line:
            return []

        for taxes in line:
            tnom = taxes.name
            tax_obj = self.pool.get('account.tax')
            tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
            tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100


report_sxw.report_sxw(
    'report.purchase.order.vauxoo',
    'purchase.order',
    'addons/purchase_report/report/order_vauxoo.rml',
    parser=purchase_vauxoo,
    header = False 
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
