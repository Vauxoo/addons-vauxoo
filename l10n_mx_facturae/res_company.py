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
from tools.translate import _
import tools
import os
import time
import release
import tempfile
import base64

class res_company_facturae_certificate(osv.osv):
    _name = 'res.company.facturae.certificate'
    
    _rec_name = 'serial_number'
    
    _columns = {
        'serial_number': fields.char('Serial Number', size=64, required=False),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'certificate_file': fields.binary('Certificate File', filters='*.cer,*.certificate,*.cert', required=True),
        'certificate_key_file': fields.binary('Certificate Key File', filters='*.key', required=True),
        'certificate_password': fields.char('Certificate Password', size=64, invisible=True, required=True),
        'certificate_file_pem': fields.binary('Certificate File PEM', filters='*.pem,*.cer,*.certificate,*.cert'),
        'certificate_key_file_pem': fields.binary('Certificate Key File PEM', filters='*.pem,*.key'),
        'date_start': fields.date('Fecha Inicio', required=False),
        'date_end': fields.date('Fecha Fin', required=True),
        'fname_xslt': fields.char('Archivo XML Parser (.xslt)', help='Ubicacion en servidor de archivo XSLT, que parsea al XML.\nPuedes ser la ruta completa o suponiendo el prefijo del "root_path\"\nDejar vacio para que el sistema tome el que esta por default.', size=256, required=False),
        'active': fields.boolean('Active'),
    }
    
    _defaults = {
        'active': lambda *a: True,
        #'fname_xslt': lambda *a: os.path.join('addons', 'l10n_mx_facturae', 'SAT', 'cadenaoriginal_2_0_l.xslt'),
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def onchange_certificate_info(self, cr, uid, ids, certificate_file, certificate_key_file, certificate_password, context=None):
        #print "ENTRO A onchange_certificate_info"
        value = {}
        certificate_file_pem = False
        certificate_key_file_pem = False
        invoice_obj = self.pool.get('account.invoice')
        if certificate_file and certificate_key_file and certificate_password:            
            certificate_file_pem, certificate_key_file_pem = self._get_pem_b64(cr, uid, ids, certificate_file, certificate_key_file, certificate_password)
            value.update({
                'certificate_file_pem': certificate_file_pem,
                'certificate_key_file_pem': certificate_key_file_pem,
            })
        return {'value': value}
    
    def _generate_pem_fname(self, cr, uid, ids, fname, type='cer', password=None):
        file_b64 = base64.encodestring( open(fname, "r").read() )
        pem_b64 = self._generate_pem_fname(cr, uid, ids, file_b64)
        return pem_b64
    
    def _read_file_attempts(self, fname, max_attempt=6, seconds_delay=0.5):
        fdata = False
        cont = 1
        while True:
            time.sleep( seconds_delay )
            try:
                fdata = open( fname, "r").read()
            except:
                pass
            if fdata or max_attempt < cont:
                break
            cont += 1
        return fdata
    
    def _generate_pem_b64(self, cr, uid, ids, file_b64, type='cer', password=None):
        invoice_obj = self.pool.get('account.invoice')
        fname = invoice_obj.binary2file(cr, uid, [], file_b64, file_prefix="openerp__", file_suffix="."+type)
        
        (fileno_pem, fname_pem) = tempfile.mkstemp('.'+type+'.pem', 'openerp_' + (type or '') + '__facturae__' )
        os.close(fileno_pem)
        pem = ''
        if type == 'cer':
            cmd = 'openssl x509 -inform DER -in %s -outform PEM -pubkey -out %s'%(fname, fname_pem)
            args = tuple( cmd.split(' ') )
            input, output = tools.exec_command_pipe(*args)
            pem = self._read_file_attempts(fname_pem, max_attempt=6, seconds_delay=0.5)
            input.close()
            output.close()
        elif type == 'key':
            (fileno_password, fname_password) = tempfile.mkstemp('.txt', 'openerp_' + (False or '') + '__facturae__' )
            os.close(fileno_password)
            open(fname_password, "w").write( password )
            
            cmd = 'openssl pkcs8 -inform DER -in %s -passin file:%s -out %s'%(fname, fname_password, fname_pem)
            args = tuple(cmd.split(' '))
            input, output = tools.exec_command_pipe(*args)
            pem = self._read_file_attempts(fname_pem, max_attempt=6, seconds_delay=0.5)
            input.close()
            output.close()
            os.unlink(fname_password)
        pem_b64 = base64.encodestring( pem or '') or False
        os.unlink(fname_pem)
        os.unlink(fname)
        return pem_b64
    
    def _get_pem_b64(self, cr, uid, ids, file_cer_b64, file_key_b64, password):
        cer_pem_b64 = self._generate_pem_b64(cr, uid, ids, file_cer_b64, type='cer', password=None)
        key_pem_b64 = self._generate_pem_b64(cr, uid, ids, file_key_b64, type='key', password=password)
        return [cer_pem_b64, key_pem_b64]
        
    def _get_pem_fname(self, cr, uid, ids, fname_cer, fname_key, password):
        cer_pem_b64 = self._generate_pem_fname(cr, uid, ids, fname_cer, type='cer', password=None)
        key_pem_b64 = self._generate_pem_fname(cr, uid, ids, fname_key, type='key', password=password)
        return [cer_pem_b64, key_pem_b64]
    
    '''
    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )', 'El numero inicial (Desde), tiene que ser menor al final (Hasta)!'),
        ('number_end', 'CHECK (number_end > number_start )', 'El numero final (Hasta), tiene que ser mayor al inicial (Desde)!'),
        ('approval_number_uniq', 'UNIQUE (approval_number)', 'El numero de aprobacion tiene que ser unico'),
    ]
    
    def _check_numbers_range(self, cr, uid, ids, context=None):
        approval = self.browse(cr, uid, ids[0], context=context)
        query = """SELECT approval_1.id AS id1, approval_2.id AS id2--approval_1.number_start, approval_1.number_end, approval_2.number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start and approval_2.number_end )
            LIMIT 1
        """%( approval.sequence_id.id )
        cr.execute( query )
        res = cr.dictfetchone()
        if res:
            return False
        return True
    
    _constraints = [
        (_check_numbers_range, 'Error ! Hay rangos de numeros solapados entre aprobaciones.', ['sequence_id', 'number_start', 'number_end'])
    ]
    '''
res_company_facturae_certificate()


class res_company(osv.osv):
    _inherit = 'res.company'
    
    def ____get_current_certificate(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not field_names:
            field_names=[]
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
    
    def _get_current_certificate(self, cr, uid, ids, field_names=False, arg=False, context={}):
        if not context:
            context = {}
        res = {}.fromkeys(ids, False)
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        
        date = time.strftime('%Y-%m-%d')
        
        if context.has_key('date_work'):
            #Si existe este key, significa, que no viene de un function, si no de una invocacion de factura
            date = context['date_work']
            if not date:
                #Si existe el campo, pero no esta asignado, significa que no fue por un function, y que no se requiere la current_date
                ###print "NOTA: Se omitio el valor de date"
                return res
        for company in self.browse(cr, uid, ids, context=context):
            current_company = company
            while True:
                certificate_ids = certificate_obj.search(cr, uid, [
                        ('company_id', '=', company.id),
                        ('date_start', '<=', date),
                        ('date_end', '>=', date),
                        ('active', '=', True),
                    ], limit=1)
                certificate_id = certificate_ids and certificate_ids[0] or False
                company = company.parent_id
                if certificate_id or not company:
                    break
            res[current_company.id] = certificate_id
        return res
    
    """
    def copy(self, cr, uid, id, default={}, context={}, done_list=[], local=False):
        if not default:
            default = {}
        default = default.copy()
        default['certificate_ids'] = False
        return super(res_company, self).copy(cr, uid, id, default, context=context)
    """
    
    _columns = {
        'certificate_ids': fields.one2many('res.company.facturae.certificate', 'company_id', 'Certificates'),
        'certificate_id': fields.function(_get_current_certificate, method=True, type='many2one', relation='res.company.facturae.certificate', string='Certificate Current'), 
        'cif_file': fields.binary('Cedula de Identificacion Fiscal'),
        'invoice_out_sequence_id': fields.many2one('ir.sequence', 'Invoice Out Sequence', \
            help="The sequence used for invoice out numbers."),
        'invoice_out_refund_sequence_id': fields.many2one('ir.sequence', 'Invoice Out Refund Sequence', \
            help="The sequence used for invoice out refund numbers."),
    }
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
