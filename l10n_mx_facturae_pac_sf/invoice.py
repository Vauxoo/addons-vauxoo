# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
from openerp.tools.misc import ustr
import wizard
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    _columns = {
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello', help='Sign assigned by the SAT'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32,
                                           help='Serial Number of the Certificate'),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original',
                                            help='Original String used in the electronic invoice'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado',
                                               help='Date when is stamped the electronic invoice'),
        'cfdi_fecha_cancelacion': fields.datetime('CFD-I Fecha Cancelacion',
                                                  help='If the invoice is cancel, this field saved the date when is cancel'),
        'cfdi_folio_fiscal': fields.char('CFD-I Folio Fiscal', size=64,
                                         help='Folio used in the electronic invoice'),
    }

    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context=None):
        """
        @params cfdi_data : * TODO
        """
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attachment_obj = self.pool.get('ir.attachment')
        cfdi_xml = cfdi_data.pop('cfdi_xml')
        if cfdi_xml:
            self.write(cr, uid, ids, cfdi_data)
            cfdi_data[
                'cfdi_xml'] = cfdi_xml  # Regresando valor, despues de hacer el write normal
            """for invoice in self.browse(cr, uid, ids):
                #fname, xml_data = self.pool.get('account.invoice').\
                    _get_facturae_invoice_xml_data(cr, uid, [inv.id],
                    context=context)
                fname_invoice = invoice.fname_invoice and invoice.\
                    fname_invoice + '.xml' or ''
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( cfdi_xml or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
                attachment_ids = attachment_obj.search(cr, uid, [('name','=',\
                    fname_invoice),('res_model','=','account.invoice'),(
                    'res_id', '=', invoice.id)])
                if attachment_ids:
                    attachment_obj.write(cr, uid, attachment_ids, data_attach,
                        context=context)
                else:
                    attachment_obj.create(cr, uid, data_attach, context=context)
                """
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'cfdi_cbb': False,
            'cfdi_sello': False,
            'cfdi_no_certificado': False,
            'cfdi_cadena_original': False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
    """
    TODO: reset to draft considerated to delete these fields?
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'cfdi_cbb': False,
            'cfdi_sello':False,
            'cfdi_no_certificado':False,
            'cfdi_cadena_original':False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).action_cancel_draft(cr, uid, ids, args)
    """

    def _get_file(self, cr, uid, inv_ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        invoice = self.browse(cr, uid, ids, context=context)[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
            '.xml' or ''
        aids = self.pool.get('ir.attachment').search(cr, uid, [(
            'datas_fname', '=', invoice.fname_invoice+'.xml'), (
                'res_model', '=', 'account.invoice'), ('res_id', '=', id)])
        xml_data = ""
        if aids:
            brow_rec = self.pool.get('ir.attachment').browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = self._get_facturae_invoice_xml_data(
                cr, uid, inv_ids, context=context)
            self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=None)#Context, because use a variable type of our code but we dont need it.
        self.fdata = base64.encodestring(xml_data)
        msg = _("Press in the button  'Upload File'")
        return {'file': self.fdata, 'fname': fname_invoice,
                'name': fname_invoice, 'msg': msg}

    def add_node(self, node_name=None, attrs=None, parent_node=None,
                 minidom_xml_obj=None, attrs_types=None, order=False):
        """
            @params node_name : Name node to added
            @params attrs : Attributes to add in node
            @params parent_node : Node parent where was add new node children
            @params minidom_xml_obj : File XML where add nodes
            @params attrs_types : Type of attributes added in the node
            @params order : If need add the params in order in the XML, add a
                    list with order to params
        """
        if not order:
            order = attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement(key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])

                key_node.appendChild(text_node)
                new_node.appendChild(key_node)
        parent_node.appendChild(new_node)
        return new_node

    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context=None):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if context is None:
            context = {}
        if xml_res_str:
            node_Addenda = xml_res_str.getElementsByTagName('cfdi:Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(
                    comprobante)[0]
                node_Addenda = self.add_node(
                    'cfdi:Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
            else:
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
        return xml_res_str

    def _get_type_sequence(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(
                cr, uid, sequence_app_id[0], context=context).type
        if 'cfdi' in type_inv:
            comprobante = 'cfdi:Comprobante'
        else:
            comprobante = 'Comprobante'
        return comprobante

    def _get_time_zone(self, cr, uid, invoice_id, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a
    
    def _get_file_cancel(self, cr, uid, inv_ids, context=None):
        if context is None:
            context = {}
        inv_ids = inv_ids[0]
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', inv_ids), (
            'name', 'ilike', '%.xml')], context=context)
        res = {}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = atta_brw.datas or False
        else:
            inv_xml = False
            raise osv.except_osv(('State of Cancellation!'), (
                "This invoice hasn't stamped, so that not possible cancel."))
        return {'file': inv_xml}

    def write_cfd_data(self, cr, uid, ids, cfd_datas, context=None):
        """
        @param cfd_datas : Dictionary with data that is used in facturae CFDI
        """
        if context is None:
            context = {}
        if not cfd_datas:
            cfd_datas = {}
        comprobante = self._get_type_sequence(cr, uid, ids, context=context)
        # obtener cfd_data con varios ids
        # for id in ids:
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if True:
            data = {}
            cfd_data = cfd_datas
            noCertificado = cfd_data.get(
                comprobante, {}).get('noCertificado', '')
            certificado = cfd_data.get(comprobante, {}).get('certificado', '')
            sello = cfd_data.get(comprobante, {}).get('sello', '')
            cadena_original = cfd_data.get('cadena_original', '')
            data = {
                'no_certificado': noCertificado,
                'certificado': certificado,
                'sello': sello,
                'cadena_original': cadena_original,
            }
            self.write(cr, uid, ids, data, context=context)
        return True
