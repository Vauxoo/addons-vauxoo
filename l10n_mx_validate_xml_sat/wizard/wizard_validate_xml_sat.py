# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.osv import osv, fields
from tools.translate import _
import decimal_precision as dp
import base64
#~ from xml.dom import minidom
#~ import xml.dom.minidom
try:
    import xmltodict
except:
    _logger.error('Execute "sudo pip install xmltodict" to use l10n_mx_facturae_report module.')
    
class wizard_validate_uuid_sat(osv.osv_memory):
    _name = 'wizard.validate.uuid.sat'
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(wizard_validate_uuid_sat, self).default_get(cr, uid, fields, context=context)
        ir_att_obj = self.pool.get('ir.attachment.facturae.mx')
        attachments = ir_att_obj.search(cr, uid, [('id_source', 'in', context['active_ids'])], context=context)
        list_xml = []
        for att in ir_att_obj.browse(cr, uid, attachments, context):
            if att.file_xml_sign:
                data_xml = base64.decodestring(att.file_xml_sign.datas)
                dict_data = dict(xmltodict.parse(data_xml).get('cfdi:Comprobante', {}))
                complemento = dict_data.get('cfdi:Complemento', {})
                list_xml.append([0, False, {
                    'name': att.file_xml_sign.name,
                    'amount': float(dict_data.get('@total', 0.0)), 
                    'number': dict_data.get('@folio', ''), 
                    'type': dict_data.get('@tipoDeComprobante', ''), 
                    'uuid': complemento.get('tfd:TimbreFiscalDigital', {}).get('@UUID', ''), 
                    'date_time': dict_data.get('@fecha', ''), 
                    'file_xml': att.file_xml_sign.id}])
        res.update({'xml_ids': list_xml})
        return res
    
    _columns = {
        'name': fields.char('Wizard name', readonly=True, size=64),
        'xml_ids': fields.many2many('xml.to.validate.line', 'wizard_xml_to_validate', 'wizard_id',
            'xml_id', 'XMLs to validate', help='XMLs to validate the uuid in the SAT'),
    }
    
class xml_to_validate_line(osv.osv_memory):
    _name = 'xml.to.validate.line'
    
    _columns = {
        'name': fields.char('XML name', readonly=True, size=64),
        'file_xml': fields.many2one('ir.attachment', 'File XML', help='File to validate UUID'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'),
            readonly=True, help='Amount to the XML'),
        'number': fields.char('Number', readonly=True, help='Number of XML'),
        'type': fields.char('Type', readonly=True, help='Type of document that generated the XML'),
        'uuid': fields.char('UUID', readonly=True, help='UUID of XML'),
        'date_time': fields.datetime('DateTime', readonly=True, help='DateTime in that was '\
            'generated the XML'),
        'result': fields.char('Result', readonly=True, help='Result of the validation'),
    }

    def onchange_xml_id(self, cr, uid, ids, xml_id, context=None):
        result = {'value': {}}
        if xml_id:
            att_obj = self.pool.get('ir.attachment')
            att_brw = att_obj.browse(cr, uid, xml_id, context=context)
            data_xml = base64.decodestring(att_brw.datas or '')
            dict_data = dict(xmltodict.parse(data_xml).get('cfdi:Comprobante', {}))
            complemento = dict_data.get('cfdi:Complemento', {})
            result['value'].update({
                'name': att_brw.name or '',
                'amount': float(dict_data.get('@total', 0.0)), 
                'number': dict_data.get('@folio', ''), 
                'type': dict_data.get('@tipoDeComprobante', ''), 
                'uuid': complemento.get('tfd:TimbreFiscalDigital', {}).get('@UUID', ''), 
                'date_time': dict_data.get('@fecha', ''), 
                })
        return result
