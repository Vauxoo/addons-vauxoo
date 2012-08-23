#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Mexico (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
import base64
import addons


class facturae_config(osv.osv_memory):
    _name = 'facturae.config'
    _inherit = 'res.config'
    _description = __doc__

    def default_get(self, cr, uid, fields_list=None, context=None):
        defaults = super(facturae_config, self).default_get(cr, uid, fields_list=fields_list, context=context)
        logo = open(addons.get_module_resource('l10n_mx_facturae', 'images', 'piramide_azteca.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def _assign_vat(self, cr, uid, vat,company_id,context=None):
        partner_id = self.pool.get('res.company').browse(cr,uid,company_id).partner_id.id
        partner_obj= self.pool.get('res.partner')
        if partner_obj.check_vat(cr,uid,[partner_id],context):
            partner_obj.write(cr, uid, partner_id,{ 
                'vat': vat,
            },context=context)

    def _write_company(self, cr, uid, cif_file,company_id,context=None):
        self.pool.get('res.company').write(cr, uid, company_id,{
            'cif_file': cif_file,
            },context=context)

    def _create_sequence(self,cr,uid,ids,context=None):
        for seq in self.pool.get('sequence.approval.config').browse(cr,uid,ids,context=context):
            seq_app = {
                'approval_number': seq.approval_number,
                'serie': seq.serie,
                'approval_year': seq.approval_year,
                'number_start': seq.number_start,
                'number_end': seq.number_end,
            }
            self.pool.get('ir.sequence').write(cr,uid,seq.journal_id.sequence_id.id,{
                'prefix':seq.serie,
                'approval_ids':[(0,0, seq_app)],
                'journal_id': seq.journal_id.id,
            },context=context)

    def execute(self, cr, uid, ids, context=None):
        company_id=self.pool.get('res.users').browse(cr,uid,[uid],context)[0].company_id.partner_id.id
        wiz_data = self.read(cr, uid, ids[0])
        if wiz_data['vat']:
            self._assign_vat(cr, uid, wiz_data["vat"],company_id,context)
        if wiz_data['cif_file']:
            self._write_company(cr, uid, wiz_data["cif_file"],company_id,context)
        if wiz_data['sequences_app']:
            self._create_sequence(cr, uid, wiz_data['sequences_app'],context)

    _columns = {
        'cif_file': fields.binary('CIF',help="Fiscal Identification Card"),
        'vat': fields.char('VAT', 64, help='Federal Register of Causes'),
        'company_id': fields.many2one('res.company',u'Company',help="Select company to assing vat and/or cif"),
        'sequences_app': fields.one2many('sequence.approval.config', 'sequence_app_id', 'Sequences for Company assigned for SAT'),
    }

facturae_config()

class sequence_detail(osv.osv_memory):
    _name = 'sequence.approval.config'
    _columns = {
        'approval_number': fields.char(u'No. Appv', size=64,help="Approval Number, which the authority designates a range of pages requested."),
        'serie': fields.char(u'Serie', size=12,),
        'approval_year': fields.char(u'Year of Approbal', size=32,help="Year that were approved series"),
        'number_start': fields.integer(u'From'),
        'number_end': fields.integer(u'To'),
        'journal_id': fields.many2one('account.journal',u'Journal',help="Journal to define the sequence approved for the SAT"),
        'sequence_app_id': fields.many2one("facturae.config", "Sequences"),
    }
sequence_detail()

class invoicee_certificate_config(osv.osv_memory):
    _name = 'invoicee.certificate.config'
    _inherit = 'res.config'

    def default_get(self, cr, uid, fields_list=None, context=None):
        defaults = super(invoicee_certificate_config, self).default_get(cr, uid, fields_list=fields_list, context=context)
        logo = open(addons.get_module_resource('l10n_mx_facturae', 'images', 'charro.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def _assign_certificate(self,cr,uid,ids,company_id,cert_file,cert_key,cert_pass,context=None):
        facte_cert = self.pool.get('res.company.facturae.certificate')
        data_facte = facte_cert.onchange_certificate_info(cr, uid, ids, cert_file, cert_key, cert_pass, context=context)
    
        if data_facte['warning']:
            osv.osv_except(data['warning']['title'], data['warning']['message'] )
        else:
            facte_cert.create(cr,uid,{
                'certificate_file':cert_file,
                'certificate_key_file':cert_key,
                'certificate_password':cert_pass,
                'date_end':data_facte['value']['date_end'],
                'date_start':data_facte['value']['date_start'],
                'certificate_file_pem':data_facte['value']['certificate_file_pem'],
                'certificate_key_file_pem':data_facte['value']['certificate_key_file_pem'],
                'serial_number':data_facte['value']['serial_number'],
                'company_id':company_id,
            },context)
        
    def execute(self, cr, uid, ids, context=None):
        company_id=self.pool.get('res.users').browse(cr,uid,[uid],context)[0].company_id.partner_id.id
        wiz_data = self.read(cr, uid, ids[0])
        if wiz_data['certificate_file'] and wiz_data['certificate_key_file'] and wiz_data['certificate_password']:
            self._assign_certificate(cr, uid, ids,company_id,wiz_data['certificate_file'],wiz_data['certificate_key_file'],wiz_data['certificate_password'],context)

    _columns = {
        'certificate_file': fields.binary('Certificate File', filters='*.cer,*.certificate,*.cert', required=True),
        'certificate_key_file': fields.binary('Certificate Key File', filters='*.key', required=True),
        'certificate_password': fields.char('Certificate Password', size=64, invisible=False, required=True),
    }
    
invoicee_certificate_config()
