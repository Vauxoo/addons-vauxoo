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

class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids, context=None):
        return []

    def _get_index(self, cr, uid, ids, context=None):
        return True

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'company_id': fields.many2one('res.company', 'Company'),
        'file_xml': fields.binary('File XML'),
        'file_xml_index': fields.text('File XML Index'),
        'file_xml_sign': fields.binary('File XML Sign'),
        'file_xml_sign_index': fields.text('File XML Sign Index'),
        'file_pdf': fields.binary('File PDF'),
        'file_pdf_index': fields.text('File PDF Index'),
        'identifier': fields.char('Identifier', size=128),
        'type': fields.selection(_get_type, 'Type', size=64),
        'state': fields.selection([
                ('draft', 'Draft'),
                ('confirm', 'Confirm'),#Generate XML
                ('sign', 'Sign'),#Generate XML Sign
                ('printable', 'Printable Format'),#Generate PDF
                ('done', 'Done'),
                ('cancel', 'Cancel'),
            ], 'State', readonly=True, required=True),
    }
    
    _defaults = {
        'state': 'draft',
    }
    
    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'})
    
    def action_sign(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sign'})

    def action_printable(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'printable'})

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
    def reset_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})
ir_attachment_facturae_mx()
