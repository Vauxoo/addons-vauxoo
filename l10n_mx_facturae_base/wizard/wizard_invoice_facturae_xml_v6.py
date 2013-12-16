# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
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

import base64
import time


class wizard_invoice_facturae_xml_v6(osv.TransientModel):
    _name = 'wizard.invoice.facturae.xml.v6'

    _columns = {
        'facturae': fields.binary('Facturae File', readonly=True),
        'facturae_fname': fields.char('File Name', size=64),
        'note': fields.text('Log'),
    }

    def _get_facturae_fname(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        res = self._get_invoice_facturae_xml(cr, uid, data, context)
        return res['facturae_fname']

    def _get_facturae(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        res = self._get_invoice_facturae_xml(cr, uid, data, context)
        return res['facturae']

    _defaults = {
        'facturae_fname': _get_facturae_fname,
        'facturae': _get_facturae,
    }

    def _get_invoice_facturae_xml(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        ids = data['active_ids']
        id = ids[0]
        invoice = invoice_obj.browse(cr, uid, [id], context=context)[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
            '.xml' or ''
        aids = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname',
            '=', invoice.fname_invoice+'.xml'), (
            'res_model', '=', 'account.invoice'), ('res_id', '=', id)])
        xml_data = ""
        if aids:
            brow_rec = self.pool.get('ir.attachment').browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, ids, context=context)
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=context)
        fdata = base64.encodestring(xml_data)
        return {'facturae': fdata, 'facturae_fname': fname_invoice, }
