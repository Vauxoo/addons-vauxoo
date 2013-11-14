# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc

import time
import os
import tempfile
import base64

msg2 = "Contact you administrator &/or info@vauxoo.com"


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_fname_invoice(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        sequence_obj = self.pool.get('ir.sequence')

        invoice_id__sequence_id = self._get_invoice_sequence(
            cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            sequence_id = invoice_id__sequence_id[invoice.id]
            sequence = False
            if sequence_id:
                sequence = sequence_obj.browse(
                    cr, uid, [sequence_id], context)[0]
            fname = ""
            fname += (invoice.company_id.partner_id and (
                'vat_split' in invoice.company_id.partner_id._columns and \
                invoice.company_id.partner_id.vat_split or \
                invoice.company_id.partner_id.vat) or '')
            fname += '_'
            number_work = invoice.number or invoice.internal_number
            try:
                context.update({'number_work': int(number_work) or False})
                fname += sequence and sequence.approval_id and \
                    sequence.approval_id.serie or ''
                fname += '_'
            except:
                pass
            fname += number_work or ''
            res[invoice.id] = fname
        return res

    _columns = {
        # Extract date_invoice from original, but add datetime
        #'date_invoice': fields.datetime('Date Invoiced', states={'open':[('readonly',True)],'close':[('readonly',True)]}, help="Keep empty to use the current date"),
        #'invoice_sequence_id': fields.function(_get_invoice_sequence, method=True, type='many2one', relation='ir.sequence', string='Invoice Sequence', store=True),
        'fname_invoice':  fields.function(_get_fname_invoice, method=True,
            type='char', size='26', string='File Name Invoice',
            help='Is a concatenation of VAT and number of invoice'),
    }

    _defaults = {
        #'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def create_report(self, cr, uid, res_ids, report_name=False, file_name=False, context=None):
        """
        @param report_name : Name of report with the name of object more type
            of report
        @param file_name : Path where is save the report temporary more the
            name of report that is 'openerp___facturae__' more six random
            characters for no files duplicate
        """
        if context is None:
            context = {}
        if not report_name or not res_ids:
            return (False, Exception('Report name and Resources ids are required !!!'))
        # try:
        ret_file_name = file_name+'.pdf'
        service = netsvc.LocalService("report."+report_name)
        (result, format) = service.create(cr, uid, res_ids, {}, {})
        fp = open(ret_file_name, 'wb+')
        fp.write(result)
        fp.close()
        # except Exception,e:
            # print 'Exception in create report:',e
            # return (False,str(e))
        return (True, ret_file_name)

    def create_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        (fileno, fname) = tempfile.mkstemp(
            '.pdf', 'openerp_' + (False or '') + '__facturae__')
        os.close(fileno)

        file = self.create_report(cr, uid, [
                                  id], "account.invoice.facturae.pdf2", fname)
        is_file = file[0]
        fname = file[1]
        if is_file and os.path.isfile(fname):
            f = open(fname, "r")
            data = f.read()
            f.close()

            data_attach = {
                'name': context.get('fname'),
                'datas': data and base64.encodestring(data) or None,
                'datas_fname': context.get('fname'),
                'description': u'Factura-E CBB PDF',
                'res_model': self._name,
                'res_id': id,
            }
            self.pool.get('ir.attachment').create(
                cr, uid, data_attach, context=context)
        return True

    """def action_cancel_draft(self, cr, uid, ids, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        for invoice in self.browse(cr, uid, ids):
            try:
                attachment_pdf_id = attachment_obj.search(cr, uid, [
                    ('name','=',invoice.fname_invoice),###no se agrega.pdf,
                        ##porque el generador de reportes, no lo hace asi,
                        ##actualmente o agrega doble .pdf o nada
                    ('datas_fname','=',invoice.fname_invoice+'.pdf'),
                    ('res_model','=','account.invoice'),
                    ('res_id','=',invoice.id)
                ], limit=1)
                attachment_obj.unlink(cr, uid, attachment_pdf_id)
            except:
                pass
        return super(account_invoice, self).action_cancel_draft(cr, uid, ids,
            context=context)
    """
