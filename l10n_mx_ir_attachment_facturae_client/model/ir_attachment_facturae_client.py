# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Sabrina Romero <sabrina@vauxoo.com>  
#    Financed by: Vauxoo Consultores <info@vauxoo.com>
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
from openerp import release
import time
import tempfile
import base64
import os
import traceback
import sys
from xml.dom import minidom
import xml.dom.minidom
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta

class ir_attachment_facturae_client(osv.Model):
    _name = 'ir.attachment.facturae.client'

    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=True,
                            help='Name of attachment generated'),
        'file_input': fields.many2one('ir.attachment', 'File input',
                                      readonly=True, help='File input'),
        'last_date': fields.datetime('Last Modified', readonly=True,
                                     help='Date when is generated the attachment'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('signed', 'Signed'),
            ('printable', 'Printable Format Generated'),
            ('sent_customer', 'Sent Customer'),
            ('sent_backup', 'Sent Backup'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'), ],
            'State', readonly=True, required=True, help='State of attachments'),
        'res_pac_id': fields.many2one('res.pac', 'Res Pac',
                                            help='Params Pac'),
        'certificate_file': fields.binary('Certificate File',
            filters='*.cer,*.certificate,*.cert', help='This file .cer is proportionate by the SAT'),
        'certificate_key_file': fields.binary('Certificate Key File',
            filters='*.key', help='This file .key is proportionate by the SAT'),
        'certificate_password': fields.char('Certificate Password', size=64,
            invisible=False, help='This password is proportionate by the SAT'),
        'company_id': fields.many2one('res.company', 'Company',
                                        help='Company to which it belongs this params pac user'),
    }

    _defaults = {
        'state': 'draft',
        'last_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'company_id': lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def stamp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_attch_obj = self.pool.get('ir.attachment')
        ir_attch_facte_obj = self.pool.get('ir.attachment.facturae.mx')
        for attachment_client in self.browse(cr, uid, ids, context=context):
             ir_attachment_values = {'name': attachment_client.file_input.name,
                                        'datas': attachment_client.file_input.datas,
                                        'datas_fname': attachment_client.file_input.datas_fname,
                                        'res_model': attachment_client.file_input.res_model,
                                        'res_id': False,
                                        }
 
             atta_id = ir_attch_obj.create(cr, uid, ir_attachment_values, context=None)
             ir_attachment_facte_values = { 'name': attachment_client.name,
                                                'id_source': False,
                                                'model_source': 'account.invoice', # This hardcore value must be changed
                                                'attachment_email': '',
                                                'certificate_password': attachment_client.certificate_password,
                                                'certificate_file': attachment_client.certificate_file,
                                                'certificate_key_file': attachment_client.certificate_key_file,
                                                'user_pac': '',
                                                'password_pac': '',
                                                'url_webservice_pac': '',
                                                'file_input': attachment_client.file_input.id,
                                                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                'res_pac': attachment_client.res_pac_id.id,
                                                }
             atta_facte_id = ir_attch_facte_obj.create(cr, uid, ir_attachment_facte_values, context=None)
             print '-----------------atta_id---------------->',atta_id
             print '------------------atta_facte_id--------------->',atta_facte_id
            
            
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
