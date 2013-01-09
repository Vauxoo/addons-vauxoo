# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

import pooler
#~ import wizard
import base64
import netsvc
from tools.translate import _
import time
from osv import osv, fields
import datetime
from dateutil.relativedelta import relativedelta

class wizard_invoice_facturae_txt_v6(osv.osv_memory):
    _name = 'wizard.invoice.facturae.txt.v6'
    
    def _get_month_selection(self, cr, uid, context=None):
        months_selection = [
            (1,'Enero'),
            (2,'Febrero'),
            (3,'Marzo'),
            (4,'Abril'),
            (5,'Mayo'),
            (6,'Junio'),
            (7,'Julio'),
            (8,'Agosto'),
            (9,'Septiembre'),
            (10,'Octubre'),
            (11,'Noviembre'),
            (12,'Diciembre'),
        ]
        return months_selection
        
    _columns = {
        'month':fields.selection(_get_month_selection, 'Mes', type="integer"),
        'year':fields.integer('Ano'),
        'date_start':fields.datetime('Fecha Inicial'),
        'date_end':fields.datetime('Fecha Final'),
        'invoice_ids':fields.many2many('account.invoice', 'invoice_facturae_txt_rel', 'invoice_id', 'facturae_id', 'Facturas', domain="[('type', 'in', ['out_invoice', 'out_refund'] )]"),
        'facturae':fields.binary('Facturae File', readonly=True),
        'facturae_fname':fields.char('File Name', size=64),
        'note':fields.text('Log', readonly=True),
    }
    
    def _get_facturae_fname(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('facturae_fname', 0)
        
    def _get_facturae(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('facturae', 0)

    def _get_note(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('note', 0)
        
    _defaults = {
        'month':lambda*a: int(time.strftime("%m"))-1,
        'year':lambda*a: int(time.strftime("%Y")),
        'date_start':lambda*a: (datetime.datetime.strptime(time.strftime('%Y-%m-01 00:00:00'), '%Y-%m-%d 00:00:00' ) - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'date_end':lambda*a: time.strftime('%Y-%m-%d 23:59:59'),
        'facturae_fname':_get_facturae_fname,
        'facturae':_get_facturae,
        'note':_get_note,
    
    }

    def get_invoices_date(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        #invoice_ids.append(19)
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        if data['invoice_ids']:
            invoice_ids = []
        else:
            invoice_ids = data['invoice_ids']
        date_start = data['date_start']
        date_end = data['date_end']
        #context.update( {'date': date_start.strftime("%Y-%m-%d")} )
        invoice_ids.extend( 
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['open', 'paid', 'cancel'] ),
                ( 'date_invoice', '>=', date_start ),
                ( 'date_invoice', '<', date_end ),
                ( 'number', '<>', False ),
            ], order='date_invoice', context=context)
        )
        invoice_ids.extend(
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['cancel'] ),
                ( 'date_invoice_cancel', '>=', date_start ),
                ( 'date_invoice_cancel', '<', date_end ),
                ( 'number', '<>', False ),
            ], order='date_invoice', context=context)
        )
        self.write(cr, uid, ids, {'invoice_ids': [(6, 0, invoice_ids)] }, context=None)
        return True
        
    def get_invoices_month(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = data['invoice_ids']
        year = data['year']
        month = int(data['month'])
        date_start = datetime.datetime(year, month, 1, 0, 0, 0)
        date_end = date_start + relativedelta(months=1)
        context.update( {'date': date_start.strftime("%Y-%m-%d")} )
        invoice_ids.extend(
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['open', 'paid', 'cancel'] ),
                ( 'date_invoice', '>=', date_start.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'date_invoice', '<', date_end.strftime("%Y-%m-%d %H:%M:%S") ),
                #( 'number', '<>', False ),
                ( 'internal_number', '<>', False ),
                ], order='date_invoice', context=context)
        )
        invoice_ids.extend(  
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['cancel'] ),
                ( 'date_invoice_cancel', '>=', date_start.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'date_invoice_cancel', '<', date_end.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'internal_number', '<>', False ),
                ], order='date_invoice', context=context)
        )
        invoice_ids = list(set(invoice_ids))
        self.write(cr, uid, ids, {'invoice_ids': [(6, 0, invoice_ids)] }, context=None)
        return True

    def create_facturae_txt(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        data = self.read(cr, uid, ids, context=context)[0]
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = data['invoice_ids']
        if invoice_ids:
            txt_data, fname = invoice_obj._get_facturae_invoice_txt_data(cr, uid, invoice_ids, context=context)
            if txt_data:
                txt_data = base64.encodestring( txt_data )
                context.update({'facturae': txt_data, 'facturae_fname': fname, 'note': _('Abra el archivo y verfique que la informacion, este correcta. Folios, RFC, montos y estatus reportados.\nAsegurese de que no este reportando folios, que no pertenecen a facturas electronicas (se pueden eliminar directamente en el archivo).\nTIP: Recuerde que este archivo tambien contiene folios de nota de credito.')})
                model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_wizard_invoice_facturae_txt_v6_form2')])
                resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                return {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'wizard.invoice.facturae.txt.v6',
                        'views': [(resource_id,'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context,
                        }
        return True
wizard_invoice_facturae_txt_v6()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
