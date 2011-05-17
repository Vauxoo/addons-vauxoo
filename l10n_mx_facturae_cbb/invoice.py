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
import tools
from tools.translate import _
import netsvc
import time
import os

class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    
    def compute(self, cr, uid, id, value, date_ref=False, context={}):
        if date_ref:
            try:
                date_ref = time.strftime('%Y-%m-%d', time.strptime(date_ref, '%Y-%m-%d %H:%M:%S'))
            except:
                pass
        return super(account_payment_term, self).compute(cr, uid, id, value, date_ref, context=context)
account_payment_term()

msg2= "Contacte a su administrador y/o a moylop260@hotmail.com"

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _order = 'date_invoice asc'
    
    def _get_invoice_sequence(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        for invoice in self.browse(cr, uid, ids):
            sequence_id = False
            company = invoice.company_id
            while True:
                if invoice.type == 'out_invoice':
                    if company._columns.has_key('invoice_out_sequence_id'):
                        sequence_id = company.invoice_out_sequence_id
                elif invoice.type == 'out_refund':
                    if company._columns.has_key('invoice_out_refund_sequence_id'):
                        sequence_id = company.invoice_out_refund_sequence_id
                company = company.parent_id
                if sequence_id or not company:
                    break
            if not sequence_id:
                if invoice.journal_id._columns.has_key('invoice_sequence_id') and invoice.journal_id.invoice_sequence_id:
                    sequence_id = invoice.journal_id.invoice_sequence_id
                elif invoice.journal_id._columns.has_key('sequence_id') and invoice.journal_id.sequence_id:
                    sequence_id = invoice.journal_id.sequence_id
            sequence_id = sequence_id and sequence_id.id or False
            if not sequence_id:
                sequence_str = 'account.invoice.' + invoice.type
                test = 'code=%s'
                cr.execute('SELECT id FROM ir_sequence WHERE '+test+' AND active=%s LIMIT 1', (sequence_str, True))
                res2 = cr.dictfetchone()
                sequence_id = res2 and res2['id'] or False
            res[invoice.id] = sequence_id
        return res
    
        
    def _get_fname_invoice(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        sequence_obj = self.pool.get('ir.sequence')
        
        invoice_id__sequence_id = self._get_invoice_sequence(cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            sequence_id = invoice_id__sequence_id[invoice.id]
            sequence = False
            if sequence_id:
                sequence = sequence_obj.browse(cr, uid, [sequence_id], context)[0]
            fname = ""
            fname += (invoice.company_id.partner_id and invoice.company_id.partner_id.vat or '')
            fname += '.'
            try:
                int(invoice.number)
                context.update({ 'number_work': invoice.number or False })
                fname += sequence and sequence.approval_id and sequence.approval_id.serie or ''
                fname += '.'
            except:
                pass
            fname += invoice.number or ''
            res[invoice.id] = fname
        return res
    
    _columns = {
        ##Extract date_invoice from original, but add datetime
        'date_invoice': fields.datetime('Date Invoiced', states={'open':[('readonly',True)],'close':[('readonly',True)]}, help="Keep empty to use the current date"),
        'invoice_sequence_id': fields.function(_get_invoice_sequence, method=True, type='many2one', relation='ir.sequence', string='Invoice Sequence', store=True),
        'fname_invoice':  fields.function(_get_fname_invoice, method=True, type='char', size='26', string='File Name Invoice'),
    }
    
    _defaults = {
        #'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def action_number(self, cr, uid, ids, *args):
        invoice_id__sequence_id = self._get_invoice_sequence(cr, uid, ids)#Linea agregada
        #Sustituye a la funcion original, es el mismo codigo, solo le agrega unas lineas, y no hacer SUPER
        cr.execute('SELECT id, type, number, move_id, reference ' \
                'FROM account_invoice ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')
        obj_inv = self.browse(cr, uid, ids)[0]
        for (id, invtype, number, move_id, reference) in cr.fetchall():
            if not number:
                tmp_context = {
                    'fiscalyear_id' : obj_inv.period_id and obj_inv.period_id.fiscalyear_id and obj_inv.period_id.fiscalyear_id.id or False,
                }
                sid = invoice_id__sequence_id[id]
                if sid:
                    number = self.pool.get('ir.sequence').get_id(cr, uid, sid, 'id=%s', context=tmp_context)
                if not number:
                    raise osv.except_osv('Warning !', 'No hay una secuencia de folios, definida !')

                if invtype in ('in_invoice', 'in_refund'):
                    ref = reference
                else:
                    ref = self._convert_ref(cr, uid, number)
                cr.execute('UPDATE account_invoice SET number=%s ' \
                        'WHERE id=%s', (number, id))
                cr.execute('UPDATE account_move SET ref=%s ' \
                        'WHERE id=%s AND (ref is null OR ref = \'\')',
                        (ref, move_id))
                cr.execute('UPDATE account_move_line SET ref=%s ' \
                        'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                        (ref, move_id))
                cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                        'FROM account_move_line ' \
                        'WHERE account_move_line.move_id = %s ' \
                            'AND account_analytic_line.move_id = account_move_line.id',
                            (ref, move_id))
        return True
    
    def create_report(self, cr, uid, res_ids, report_name=False, file_name=False):
        if not report_name or not res_ids:
            return (False,Exception('Report name and Resources ids are required !!!'))
        #try:
        ret_file_name = file_name+'.pdf'
        service = netsvc.LocalService("report."+report_name);
        (result,format) = service.create(cr, uid, res_ids, {}, {})
        fp = open(ret_file_name,'wb+');
        fp.write(result);
        fp.close();
        #except Exception,e:
            #print 'Exception in create report:',e
            #return (False,str(e))
        return (True,ret_file_name)
    
    def create_report_pdf(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        id = ids[0]
        
        (fileno, fname) = tempfile.mkstemp('.pdf', 'openerp_' + (False or '') + '__facturae__' )
        os.close( fileno )
        
        file = self.create_report(cr, uid, [id], "account.invoice.facturae.pdf", fname)
        is_file = file[0]
        fname = file[1]
        if is_file and os.path.isfile(fname):
            f = open(fname, "r")
            data = f.read()
            f.close()
            
            data_attach = {
                'name': context.get('fname'),
                'datas': data and base64.encodestring( data ) or None,
                'datas_fname': context.get('fname'),
                'description': u'Factura-E CBB PDF',
                'res_model': self._name,
                'res_id': id,
            }
            self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
        return True

    def action_move_create(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            if inv.move_id:
                continue
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': time.strftime('%Y-%m-%d %H:%M:%S')})
        return super(account_invoice, self).action_move_create(cr, uid, ids, *args)
        
    def action_cancel_draft(self, cr, uid, ids, *args):
        attachment_obj = self.pool.get('ir.attachment')
        for invoice in self.browse(cr, uid, ids):
            try:
                attachment_pdf_id = attachment_obj.search(cr, uid, [
                    ('name','=',invoice.fname_invoice),###no se agrega.pdf, porque el generador de reportes, no lo hace asi, actualmente o agrega doble .pdf o nada
                    ('datas_fname','=',invoice.fname_invoice+'.pdf'),
                    ('res_model','=','account.invoice'),
                    ('res_id','=',invoice.id)
                ], limit=1)
                attachment_obj.unlink(cr, uid, attachment_pdf_id)
            except:
                pass
        return super(account_invoice, self).action_cancel_draft(cr, uid, ids, args)
account_invoice()

class account_invoice_tax(osv.osv):
    _inherit= "account.invoice.tax"
    
    def _get_tax_data(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        for invoice_tax in self.browse(cr, uid, ids, context=context):
            res[invoice_tax.id] = {}
            tax_name = invoice_tax.name.lower().replace('.','').replace(' ', '').replace('-', '')
            tax_percent = invoice_tax.amount and invoice_tax.base and invoice_tax.amount*100/invoice_tax.base or 0.0
            if 'iva' in tax_name:
                tax_name = 'IVA'
                tax_percent = round(tax_percent, 0)#Hay problemas de decimales al calcular el iva, y hasta ahora el iva no tiene decimales
            elif 'isr' in tax_name:
                tax_name = 'ISR'
            elif 'ieps' in tax_name:
                tax_name = 'IEPS'
            res[invoice_tax.id]['name2'] = tax_name
            res[invoice_tax.id]['percent'] = tax_percent
            res[invoice_tax.id]['amount'] = invoice_tax.amount
        return res
account_invoice_tax()