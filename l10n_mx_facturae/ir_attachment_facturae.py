# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@openerp.com.ve
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
import netsvc

class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        types = [('cfd20', 'CFD 2.0'), ('cfd22', 'CFD 2.2'), ('cfdi30', 'CFDI 3.0'), ('cfdi32', 'CFDI 3.2'), ('cbb', 'CBB'),]
        return types

    def _get_index(self, cr, uid, ids, context=None):
        return True

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'company_id': fields.many2one('res.company', 'Company'),
        #'pac_id': ,Ver si no genera dependencia del modelo de pac
        #'file_input': fields.binary('File input'),#TODO: Agregar readonly dependiendo del state
        'file_input': fields.many2one('ir.attachment', 'File input'),
        'file_input_index': fields.text('File input'),
        #'file_xml_sign': fields.binary('File XML Sign'),
        'file_xml_sign': fields.many2one('ir.attachment', 'File XML Sign'),
        'file_xml_sign_index': fields.text('File XML Sign Index'),
        #'file_pdf': fields.binary('File PDF'),
        'file_pdf': fields.many2one('ir.attachment', 'File PDF'),
        'file_pdf_index': fields.text('File PDF Index'),
        'identifier': fields.char('Identifier', size=128),
        'type': fields.selection(_get_type, 'Type', type='char', size=64),
        'description': fields.text('Description'),
        #'invoice_type': fields.ref(),#referencia al tipo de factura
        'msj': fields.char('Last Message', size=256),
        'last_date': fields.datetime('Last Modified'),
        'state': fields.selection([
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),#Generate XML
                ('signed', 'Signed'),#Generate XML Sign
                ('printable', 'Printable Format Generated'),#Generate PDF
                ('sent_customer', 'Sent Customer'),
                ('sent_backup', 'Sent Backup'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ], 'State', readonly=True, required=True),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def action_confirm(self, cr, uid, ids, context=None):
        print "entro"
        #invoice = self.browse(cr, uid, ids, context=context)
        #id=self.pool.get('account.invoice')._get_facturae_invoice_xml_data(cr, uid, ids, context=context)
        #print id
        #certificate_id = self.pool.get('res.company')._get_current_certificate(cr, uid, [invoice.invoice_id.id], context=context)[invoice.company_id.id]
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def action_sign(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'signed'})

    def action_printable(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'printable'})

    def action_send_customer(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_customer'})

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'})

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def reset_to_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for row in self.browse(cr, uid, ids, context=context):
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'ir.attachment.facturae.mx', row.id, cr)
            wf_service.trg_create(uid, 'ir.attachment.facturae.mx', row.id, cr)
        return self.write(cr, uid, ids, {'state': 'draft'})
ir_attachment_facturae_mx()
