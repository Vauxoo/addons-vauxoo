#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
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
################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools,  netsvc
import xml
import base64
import time

class ir_attachment_facturae_mx(osv.Model):

    _inherit = 'ir.attachment.facturae.mx'

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal'),
        'payroll_id': fields.many2one('hr.payslip', 'Payslip'),
    }
    
    def signal_confirm(self, cr, uid, ids, context=None):
        from l10n_mx_facturae_lib import facturae_lib
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if msj:
            raise osv.except_osv(_('Warning'),_(msj))
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        hr_payslip_obj = self.pool.get('hr.payslip')
        attachment_obj = self.pool.get('ir.attachment')
        attach = self.browse(cr, uid, ids[0])
        msj = ''
        index_xml = ''
        type = attach.type
        status = False
        for data in self.browse(cr, uid, ids, context=context):
            if data.payroll_id:
                if 'cfdi' in type:
                    fname_invoice = data.payroll_id and data.payroll_id.name + \
                        '_V3_2_payroll.xml' or ''
                    fname, xml_data = hr_payslip_obj._get_facturae_payroll_xml_data(
                        cr, uid, [data.payroll_id.id], context=context)
                    attach = attachment_obj.create(cr, uid, {
                        'name': fname_invoice,
                        'datas': base64.encodestring(xml_data),
                        'datas_fname': fname_invoice,
                        'res_model': 'hr.payslip',
                        'res_id': data.payroll_id.id
                    }, context=context)
                    msj = _("Attached Successfully XML CFDI 3.2\n")
                    status = True
                else:
                    raise osv.except_osv(_("Type Electronic Invoice Unknow!"), _(
                            "The Type Electronic Invoice:" + (type or '')))
                if status:
                    doc_xml = xml.dom.minidom.parseString(xml_data)
                    index_xml = doc_xml.toprettyxml()
                    self.write(cr, uid, ids,
                               {'file_input': attach or False,
                                   'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                   'msj': msj,
                                   'file_input_index': index_xml}, context=context)
                    wf_service.trg_validate(uid, self._name, ids[0], 'action_confirm', cr)
                    #wf_service.trg_validate(uid, 'hr.payslip', data.payroll_id.id, 'hr_verify_sheet', cr)
            else:
                status = super(ir_attachment_facturae_mx, self).signal_confirm(cr, uid, ids, context=context)
        return status
