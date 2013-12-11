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
from openerp import pooler, tools, release

import os
import time
import tempfile
import base64


class res_company_facturae_certificate(osv.Model):
    _name = 'res.company.facturae.certificate'

    _rec_name = 'serial_number'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where you add this certificate'),
        'certificate_file': fields.binary('Certificate File',
            filters='*.cer,*.certificate,*.cert', required=True,
            help='This file .cer is proportionate by the SAT'),
        'certificate_key_file': fields.binary('Certificate Key File',
            filters='*.key', required=True, help='This file .key is \
            proportionate by the SAT'),
        'certificate_password': fields.char('Certificate Password', size=64,
            invisible=False, required=True, help='This password is \
            proportionate by the SAT'),
        'certificate_file_pem': fields.binary('Certificate File PEM',
            filters='*.pem,*.cer,*.certificate,*.cert', help='This file is \
            generated with the file.cer'),
        'certificate_key_file_pem': fields.binary('Certificate Key File PEM',
            filters='*.pem,*.key', help='This file is generated with the \
            file.key'),
        'date_start': fields.date('Date Start', required=False, help='Date \
            start the certificate before the SAT'),
        'date_end': fields.date('Date End', required=True, help='Date end of \
            validity of the certificate'),
        'serial_number': fields.char('Serial Number', size=64, required=True,
            help='Number of serie of the certificate'),
        'fname_xslt': fields.char('File XML Parser (.xslt)', size=256,
            required=False, help='Folder in server with XSLT file',
        # TODO, translate to english and later translate to spanish, que
        # parsea al XML.\nPuedes ser la ruta completa o suponiendo el
        # prefijo del "root_path\"\nDejar vacio para que el sistema tome el
        # que esta por default.'
        ),
        'active': fields.boolean('Active', help='Indicate if this certificate \
            is active'),
    }

    _defaults = {
        'active': lambda *a: True,
        #'fname_xslt': lambda *a: os.path.join('addons', 'l10n_mx_facturae', 'SAT', 'cadenaoriginal_2_0_l.xslt'),
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company'\
            )._company_default_get(cr, uid, 'res.company.facturae.certificate',
            context=c),
    }

    def get_certificate_info(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        certificate = self.browse(cr, uid, ids, context=context)[0]
        cer_der_b64str = certificate.certificate_file
        key_der_b64str = certificate.certificate_key_file
        password = certificate.certificate_password
        data = self.onchange_certificate_info(
            cr, uid, ids, cer_der_b64str, key_der_b64str, password, context=context)
        if data['warning']:
            raise osv.except_osv(data['warning'][
                                 'title'], data['warning']['message'])
        return self.write(cr, uid, ids, data['value'], context)

    def onchange_certificate_info(self, cr, uid, ids, cer_der_b64str = None,
        key_der_b64str = None, password = None, context = None):
        """
        @param cer_der_b64str : File .cer in Base 64
        @param key_der_b64str : File .key in Base 64
        @param password : Password inserted in the certificate configuration
        """
        if context is None:
            contex={}
        certificate_lib = self.pool.get('facturae.certificate.library')
        value = {}
        warning = {}
        certificate_file_pem = False
        certificate_key_file_pem = False
        invoice_obj = self.pool.get('account.invoice')
        if cer_der_b64str and key_der_b64str and password:
            fname_cer_der = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                cer_der_b64str, file_suffix='.der.cer',
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context )
            fname_key_der = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                key_der_b64str, file_suffix='.der.key',
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context)
            fname_password = certificate_lib.b64str_to_tempfile(cr, uid, ids, 
                base64.encodestring(password), file_suffix='der.txt', 
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context)
            fname_tmp = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                '', file_suffix='tmp.txt', file_prefix='openerp__' + (
                False or '') + '__ssl__', context=context)

            cer_pem = certificate_lib._transform_der_to_pem(
                fname_cer_der, fname_tmp, type_der='cer')
            cer_pem_b64 = base64.encodestring(cer_pem)

            key_pem = certificate_lib._transform_der_to_pem(
                fname_key_der, fname_tmp, fname_password, type_der='key')
            key_pem_b64 = base64.encodestring(key_pem)

            # date_fmt_return='%Y-%m-%d %H:%M:%S'
            date_fmt_return = '%Y-%m-%d'
            serial = False
            try:
                serial = certificate_lib._get_param_serial(cr, uid, ids,
                    fname_cer_der, fname_tmp, type='DER')
                value.update({
                    'serial_number': serial,
                })
            except:
                pass
            date_start = False
            date_end = False
            try:
                dates = certificate_lib._get_param_dates(cr, uid, ids, fname_cer_der,
                    fname_tmp, date_fmt_return=date_fmt_return, type='DER')
                date_start = dates.get('startdate', False)
                date_end = dates.get('enddate', False)
                value.update({
                    'date_start': date_start,
                    'date_end': date_end,
                })

            except:
                pass
            os.unlink(fname_cer_der)
            os.unlink(fname_key_der)
            os.unlink(fname_password)
            os.unlink(fname_tmp)

            if not key_pem_b64 or not cer_pem_b64:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You certificate file, key file or password is incorrect.\nVerify uppercase and lowercase')
                }
                value.update({
                    'certificate_file_pem': False,
                    'certificate_key_file_pem': False,
                })
            else:
                value.update({
                    'certificate_file_pem': cer_pem_b64,
                    'certificate_key_file_pem': key_pem_b64,
                })
        return {'value': value, 'warning': warning}

    '''
    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )',\
            'El numero inicial (Desde), tiene que ser menor al final (Hasta)!'),
        ('number_end', 'CHECK (number_end > number_start )',\
            'El numero final (Hasta), tiene que ser mayor al inicial (Desde)!'),
        ('approval_number_uniq', 'UNIQUE (approval_number)',
            'El numero de aprobacion tiene que ser unico'),
    ]

    def _check_numbers_range(self, cr, uid, ids, context=None):
        approval = self.browse(cr, uid, ids[0], context=context)
        query = """SELECT approval_1.id AS id1, approval_2.id AS \
            id2--approval_1.number_start, approval_1.number_end,
            approval_2.number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start \
                and approval_2.number_end )
            LIMIT 1
        """%( approval.sequence_id.id )
        cr.execute( query )
        res = cr.dictfetchone()
        if res:
            return False
        return True

    _constraints = [
        (_check_numbers_range, 'Error ! Hay rangos de numeros solapados entre \
            aprobaciones.', ['sequence_id', 'number_start', 'number_end'])
    ]
    '''


class res_company(osv.Model):
    _inherit = 'res.company'

    def ____get_current_certificate(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        if not field_names:
            field_names = []
        res = {}
        for id in ids:
            if "tiny" in release.name:
                res[id] = False
                field_names = [field_names]
            else:
                res[id] = {}.fromkeys(field_names, False)
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        date = context.get('date', False) or time.strftime('%Y-%m-%d')
        for company in self.browse(cr, uid, ids, context=context):
            certificate_ids = certificate_obj.search(cr, uid, [
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            for f in field_names:
                if f == 'certificate_id':
                    if "tiny" in release.name:
                        res[company.id] = certificate_id
                    else:
                        res[company.id][f] = certificate_id
        return res

    def _get_current_certificate(self, cr, uid, ids, field_names=False, arg=False, context=None):
        if context is None:
            context = {}
        res = {}.fromkeys(ids, False)
        certificate_obj = self.pool.get('res.company.facturae.certificate')

        date = time.strftime('%Y-%m-%d')

        if 'date_work' in context:
            # Si existe este key, significa, que no viene de un function, si no
            # de una invocacion de factura
            date = context['date_work']
            if not date:
                # Si existe el campo, pero no esta asignado, significa que no fue por un function, y que no se requiere la current_date
                # print "NOTA: Se omitio el valor de date"
                return res
        for company in self.browse(cr, uid, ids, context=context):
            current_company = company
            certificate_ids = certificate_obj.search(cr, uid, [
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            res[current_company.id] = certificate_id
        return res

    """
    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        if not default:
            default = {}
        default = default.copy()
        default['certificate_ids'] = False
        return super(res_company, self).copy(cr, uid, id, default, context=context)
    """

    _columns = {
        'certificate_ids': fields.one2many('res.company.facturae.certificate',
            'company_id', 'Certificates', help='Certificates configurated in \
            this company'),
        'certificate_id': fields.function(_get_current_certificate, method=True,
            type='many2one', relation='res.company.facturae.certificate',
            string='Certificate Current', help='Serial Number of the \
            certificate active and inside of dates in this company'),
        #'cif_file': fields.binary('Cedula de Identificacion Fiscal'),
        'invoice_out_sequence_id': fields.many2one('ir.sequence',
            'Invoice Out Sequence', help="The sequence used for invoice out \
            numbers."),
        'invoice_out_refund_sequence_id': fields.many2one('ir.sequence',
            'Invoice Out Refund Sequence', help="The sequence used for \
            invoice out refund numbers."),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
