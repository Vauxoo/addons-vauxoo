# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
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

from osv import osv
from osv import fields
import base64
import netsvc

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context={}):
        super(account_invoice, self).cfdi_data_write(cr, uid, ids, cfdi_data, context)
        attachment_obj = self.pool.get('ir.attachment')
        for invoice in self.browse(cr, uid, ids):
            report_name = 'account.invoice.facturae.pdf'
            service = netsvc.LocalService("report."+report_name)
            (result,format) = service.create(cr, uid, [invoice.id], {}, {})
            attachment_ids = attachment_obj.search(cr, uid, [('res_model','=','account.invoice'),('res_id', '=', invoice.id)])
            attachment_obj.file_ftp(cr,uid,attachment_ids,context)
        return True
        
account_invoice()






