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
from openerp.osv import fields, osv
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
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
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

    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context={}):
        """
        @params cfdi_data : * TODO
        """
        if not context:
            context = {}
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

    def _get_file(self, cr, uid, inv_ids, context={}):
        if not context:
            context = {}
        id = inv_ids[0]
        invoice = self.browse(cr, uid, [id], context=context)[0]
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
            }, context=context)
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

    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context={}):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if xml_res_str:
            node_Addenda = xml_res_str.getElementsByTagName('Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(
                    comprobante)[0]
                node_Addenda = self.add_node(
                    'Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
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
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(
                cr, uid, sequence_app_id[0], context=context).type
        if type_inv == 'cfdi32':
            comprobante = 'cfdi:Comprobante'
        else:
            comprobante = 'Comprobante'
        return comprobante
        
        
    def _get_time_zone(self, cr, uid, invoice_id, context=None):
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a=0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year,now.month,now.day,
                now.hour,now.minute,now.second))
            timezone_loc=(loc_dt.strftime(fmt))
            diff_timezone_original=timezone_loc[-5:-2]
            timezone_original=int(diff_timezone_original)
            s= str(datetime.now(pytz.timezone(userstz)))
            s=s[-6:-3]
            timezone_present=int(s)*-1
            a=  timezone_original + ((timezone_present + timezone_original)*-1)
        return a


    def _upload_ws_file(self, cr, uid, inv_ids, fdata=None, context={}):
        """
        @params fdata : File.xml codification in base64
        """
        comprobante = self._get_type_sequence(
            cr, uid, inv_ids, context=context)
        pac_params_obj = self.pool.get('params.pac')
        cfd_data = base64.decodestring(fdata or self.fdata)
        xml_res_str = xml.dom.minidom.parseString(cfd_data)
        xml_res_addenda = self.add_addenta_xml(
            cr, uid, xml_res_str, comprobante, context=context)
        xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
        compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
        date = compr.attributes['fecha'].value
        date_format = datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        context['date'] = date_format
        invoice_ids = inv_ids
        invoice = self.browse(cr, uid, invoice_ids, context=context)[0]
        currency = invoice.currency_id.name
        currency_enc = currency.encode('UTF-8', 'strict')
        rate = invoice.currency_id.rate and (1.0/invoice.currency_id.rate) or 1
        file = False
        msg = ''
        status = ''
        cfdi_xml = False
        pac_params_ids = pac_params_obj.search(cr, uid, [
            ('method_type', '=', 'pac_sf_firmar'), (
            'company_id', '=', invoice.company_emitter_id.id), (
            'active', '=', True)], limit=1, context=context)
        if pac_params_ids:
            pac_params = pac_params_obj.browse(
                cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace
            if 'testing' in wsdl_url:
                msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n')
            wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
            if True:  # if wsdl_client:
                file_globals = self._get_file_globals(
                    cr, uid, invoice_ids, context=context)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring(
                    open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring(
                    open(fname_key_no_pem, "r").read()) or ''
                cfdi = base64.encodestring(
                    xml_res_str_addenda.replace(codecs.BOM_UTF8, ''))
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                params = [
                    user, password, cfdi, cerCSD, keyCSD, contrasenaCSD, zip]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                resultado = wsdl_client.timbrar(*params)
                htz=int(self._get_time_zone(cr, uid, inv_ids, context=context))
                msg += resultado['resultados'] and resultado[
                    'resultados']['mensaje'] or ''
                codigo_timbrado = resultado['status'] or ''
                codigo_validacion = resultado['resultados'] and resultado[
                    'resultados']['status'] or ''
                if codigo_timbrado == '311' or codigo_validacion == '311':
                    raise osv.except_osv(_('Warning'), _('Unauthorized'))
                if codigo_timbrado == '312' or codigo_validacion == '312':
                    raise osv.except_osv(_('Warning'), _('Failed to consult the SAT'))
                if codigo_timbrado == '200':
                    msg += _(u"The validation process is completed successfully.\n")
                    if codigo_validacion == '301':
                        raise osv.except_osv(_('Warning'), _('El CFDI no tiene una estructura XML correcta'))
                    elif codigo_validacion == '302':
                        raise osv.except_osv(_('Warning'), _('El sello del emisor no es válido'))
                    elif codigo_validacion == '303':
                        raise osv.except_osv(_('Warning'), _('El Certificado de Sello Digital no corresponde al contribuyente emisor'))
                    elif codigo_validacion == '304':
                        raise osv.except_osv(_('Warning'), _('El certificado se encuentra revocado o caducó'))
                    elif codigo_validacion == '305':
                        raise osv.except_osv(_('Warning'), _('La fecha del CFDI está fuera del rango de la validez del certificado'))
                    elif codigo_validacion == '306':
                        raise osv.except_osv(_('Warning'), _('El certificado usado para generar el sello digital no es un Certificado de Sello Digital'))
                    elif codigo_validacion == '307':
                        raise osv.except_osv(_('Warning'), _('El CFDI ya ha ha sido timbrado previamente'))
                    elif codigo_validacion == '308':
                        raise osv.except_osv(_('Warning'), _('El certificado utilizado para generar el sello digital no ha sido emitido por el SAT'))
                    elif codigo_validacion == '401':
                        raise osv.except_osv(_('Warning'), _('La fecha del comprobante está fuera del rango de timbrado permitido.Han pasado mas de 72 horas desde la fecha de generacion del comprobante'))
                    elif codigo_validacion == '402':
                        raise osv.except_osv(_('Warning'), _('El contribuyente no se encuentra dentro del régimen fiscal para emitir CFDI'))
                    elif codigo_validacion == '403':
                        raise osv.except_osv(_('Warning'), _('La fecha de emisión del CFDI no puede ser anterior al 1 de enero de 2011'))
                    elif codigo_validacion == '611':
                        raise osv.except_osv(_('Warning'), _('Los datos recibidos estan incompletos o no se encuentran donde se esperarían'))
                    elif codigo_validacion == '612':
                        raise osv.except_osv(_('Warning'), _('El archivo XML o alguno de sus atributos está malformado'))
                    elif codigo_validacion == '630':
                        raise osv.except_osv(_('Warning'), _('Se han agotado los timbres de la implementacion'))
                    elif codigo_validacion == '631':
                        raise osv.except_osv(_('Warning'), _('Se han agotado los timbres del emisor'))
                    elif codigo_validacion == '632':
                        raise osv.except_osv(_('Warning'), _('Se ha alcanzado el límite de uso justo permitido por transacción'))
                    elif codigo_validacion == '633':
                        raise osv.except_osv(_('Warning'), _('Uso indebido de cuenta de producción en pruebas o cuenta de prueba en producción'))
                    elif codigo_validacion == '200':
                        msg += _(u"CFDI correctly validated and ringing.\n")
                        fecha_timbrado = resultado[
                        'resultados']['fechaTimbrado'] or False
                        fecha_timbrado = fecha_timbrado and time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.strptime(
                        fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                        fecha_timbrado = fecha_timbrado and datetime.strptime(
                        fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(
                        hours=htz) or False
                        cfdi_data = {
                        'cfdi_cbb': resultado['resultados']['qrCode'] or False,  # ya lo regresa en base64
                        'cfdi_sello': resultado['resultados'][
                            'selloSAT'] or False,
                        'cfdi_no_certificado': resultado['resultados'][
                            'certificadoSAT'] or False,
                        'cfdi_cadena_original': resultado['resultados'][
                            'cadenaOriginal'] or False,
                        'cfdi_fecha_timbrado': fecha_timbrado,
                        'cfdi_xml': base64.decodestring(resultado[
                            'resultados']['cfdiTimbrado'] or ''),  # este se necesita en uno que no es base64
                        'cfdi_folio_fiscal': resultado['resultados']['uuid'] or '',
                        }
                        if cfdi_data.get('cfdi_xml', False):
                            url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->' % (
                                comprobante)
                            cfdi_data['cfdi_xml'] = cfdi_data[
                                'cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                            file = base64.encodestring(
                                cfdi_data['cfdi_xml'] or '')
                            # self.cfdi_data_write(cr, uid, [invoice.id],
                            # cfdi_data, context=context)
                            cfdi_xml = cfdi_data.pop('cfdi_xml')
                        if cfdi_xml:
                            self.write(cr, uid, inv_ids, cfdi_data)
                            cfdi_data['cfdi_xml'] = cfdi_xml
                            msg = msg + _("\nMake Sure to the file \
                            really has generated correctly to the \
                            SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                        else:
                            msg += _(u"\nCan't extract the file XML of PAC")
                elif codigo_timbrado == '500':
                    raise osv.except_osv(_('Warning'), _('Errors occurred were not allowed to complete the process of validation / certification'))
                elif codigo_timbrado == '501':
                    raise osv.except_osv(_('Warning'), _('Failed to Connect to the database'))
                elif codigo_timbrado == '502':
                    raise osv.except_osv(_('Warning'), _('It failed when trying to retrieve or store information in the database'))
                elif codigo_timbrado == '503':
                    raise osv.except_osv(_('Warning'), _('It has reached the limit of concurrent access licenses database'))
                elif codigo_timbrado == '601':
                    raise osv.except_osv(_('Warning'), _('Authentication failed, user name or password is incorrect'))
                elif codigo_timbrado == '602':
                    raise osv.except_osv(_('Warning'), _('The user account is locked'))
                elif codigo_timbrado == '603':
                    raise osv.except_osv(_('Warning'), _('The account password has expired'))
                elif codigo_timbrado == '604':
                    raise osv.except_osv(_('Warning'), _('You have exceeded the maximum number of failed authentication attempts'))
                elif codigo_timbrado == '605':
                    raise osv.except_osv(_('Warning'), _('The user is inactive'))
                elif codigo_timbrado == '1401':
                    raise osv.except_osv(_('Warning'), _('The XML Namespace does not match the namespace of CFDI'))
                elif codigo_timbrado == '1402':
                    raise osv.except_osv(_('Warning'), _('No data found in the CFDI issuer'))
                elif codigo_timbrado == '1403':
                    raise osv.except_osv(_('Warning'), _('No data are receiver in the CFDI'))
        else:
            msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
            raise osv.except_osv(_('Warning'), _('Not found information from web services of PAC, verify that the configuration of PAC is correct'))
        return {'file': file, 'msg': msg, 'status': status, 'cfdi_xml': cfdi_xml}

    def _get_file_cancel(self, cr, uid, inv_ids, context={}):
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

    def sf_cancel(self, cr, uid, inv_ids, context=None):
        msg_global = ''
        msg_tecnical = ''
        msg_SAT = ''
        msg_status = {}
        context_id = inv_ids[0]
        company_obj = self.pool.get('res.company.facturae.certificate')
        pac_params_obj = self.pool.get('params.pac')
        invoice_brw = self.browse(cr, uid, context_id, context)
        company_brw = company_obj.browse(cr, uid, [
                            invoice_brw.company_id.id], context)[0]
        pac_params_srch = pac_params_obj.search(cr, uid, [(
            'method_type', '=', 'pac_sf_cancelar'), ('company_id', '=',
            invoice_brw.company_emitter_id.id), ('active', '=', True)],
            context=context)
        if pac_params_srch:
            pac_params_brw = pac_params_obj.browse(
                cr, uid, pac_params_srch, context)[0]
            user = pac_params_brw.user
            password = pac_params_brw.password
            wsdl_url = pac_params_brw.url_webservice
            namespace = pac_params_brw.namespace
            #---------constantes
            #~ user = 'testing@solucionfactible.com'
            #~ password = 'timbrado.SF.16672'
            #~ wsdl_url = 'http://testing.solucionfactible.com/ws/services/Timbrado?wsdl'
            #~ namespace = 'http://timbrado.ws.cfdi.solucionfactible.com'
            wsdl_client = False
            wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
            if True:  # if wsdl_client:
                file_globals = self._get_file_globals(
                    cr, uid, [context_id], context=context)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring(
                    open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring(
                    open(fname_key_no_pem, "r").read()) or ''
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                uuids = invoice_brw.cfdi_folio_fiscal  # cfdi_folio_fiscal
                params = [
                    user, password, uuids, cerCSD, keyCSD, contrasenaCSD]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                result = wsdl_client.cancelar(*params)
                codigo_cancel = result['status'] or ''
                status = result['resultados'] and result[
                    'resultados']['status'] or ''
                uuid_nvo = result['resultados'] and result[
                    'resultados']['uuid'] or ''
                msg_nvo = result['resultados'] and result[
                    'resultados']['mensaje'] or ''
                status_uuid = result['resultados'] and result[
                    'resultados']['statusUUID'] or ''
                if 'testing' in wsdl_url:
                    msg_global = _('- Status of response of SAT unknown')
                if codigo_cancel == '200':
                    msg_global += _(u"\nThe cancellation process has \
                                    been completed successfully\n")
                    if status == '201':
                        msg_global += _(u"\nFolio has been canceled \
                                                    successfully\n")
                        folio_cancel = result['resultados'] and result[
                            'resultados']['uuid'] or ''
                        msg_global = _('\n- The process of cancellation\
                                has completed correctly.\n- The uuid \
                                cancelledis: ') + folio_cancel+_(
                                    '\n\nMessage Technical:\n')
                        msg_tecnical = 'Status:', status, ' uuid:', uuid_nvo,\
                            ' msg:', msg_nvo, 'Status uuid:', status_uuid
                    elif status == '202':
                        raise osv.except_osv(_('Warning'), _('The CFDI had been previously canceled'))
                    elif status == '202':
                        raise osv.except_osv(_('Warning'), _('The CFDI had been previously canceled'))
                    elif status == '203':
                        raise osv.except_osv(_('Warning'), _('UUID does not correspond to the issuer'))
                    elif status == '204':
                        raise osv.except_osv(_('Warning'), _('The cancellation does not apply to CFDI'))
                    elif status == '205':
                        raise osv.except_osv(_('Warning'), _('The UUID does not exist or has been prosecuted for the SAT'))
                    elif status == '402':
                        raise osv.except_osv(_('Warning'), _('The Taxpayer not found the LCO or validity of obligations is reported as negative'))
                elif codigo_cancel == '601':
                    raise osv.except_osv(_('Warning'), _('Authentication failed, user name or password is incorrect'))
                elif codigo_cancel == '602':
                    raise osv.except_osv(_('Warning'), _('The user account is locked'))
"""603 - La contraseña de la cuenta ha expirado.
604 - Se ha superado el número máximo permitido de intentos fallidos de autenticación.
605 - El usuario se encuentra inactivo
611 - No se han proporcionado UUIDs a cancelar.
1701 - La llave privada y la llave pública del CSD no corresponden.
1702 - La llave privada de la contraseña es incorrecta.
1703 - La llave privada no cumple con la estructura esperada.
1704 - La llave Privada no es una llave RSA.
1710 - La estructura del certificado no cumple con la estructura X509 esperada.
1711 - El certificado no esá vigente todavía.
1712 - El certificado ha expirado.
1713 - La llave pública contenida en el certificado no es una llave RSA.
1803 - El dato no es un UUID válido."""
                if status_uuid == '201':
                    msg_SAT = _(
                        '- Status of response of the SAT: 201. The folio was canceled with success.')
                    self.write(cr, uid, context_id, {'cfdi_fecha_cancelacion':\
                    time.strftime('%Y-%m-%d %H:%M:%S')})
                elif status_uuid == '202':
                    msg_SAT = _(
                        '- Status of response of the SAT: 202. The folio already has cancelled previously.')
                elif status_uuid == '203':
                    msg_SAT = _(
                        '- Status of response of the SAT: 203. The voucher that tries cancel not corresponds the taxpayer with that signed the request of cancellation.')
                elif status_uuid == '204':
                    msg_SAT = _(
                        '- Status of response of the SAT: 204. The CFDI not aply for cancellation.')
                elif status_uuid == '205':
                    msg_SAT = _(
                        '- Status of response of the SAT: 205. Not found the folio of CFDI for his cancellation.')
        else:
            msg_global = _(
                'Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        msg_global_all = msg_SAT + msg_global + str(msg_tecnical)
        return {'message': msg_global_all, 'msg_SAT': msg_SAT, 'msg_tecnical': msg_tecnical, 'msg_global': msg_global, 'status': status, 'status_uuid': status_uuid}

    def write_cfd_data(self, cr, uid, ids, cfd_datas, context={}):
        """
        @param cfd_datas : Dictionary with data that is used in facturae CFDI
        """
        if not cfd_datas:
            cfd_datas = {}
        comprobante = self._get_type_sequence(cr, uid, ids, context=context)
        # obtener cfd_data con varios ids
        # for id in ids:
        id = ids[0]
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
            self.write(cr, uid, [id], data, context=context)
        return True
