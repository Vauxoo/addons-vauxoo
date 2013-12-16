#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Mexico (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
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
from openerp.tools.translate import _
from openerp.osv import fields, osv
import base64
from openerp import addons


class facturae_config(osv.TransientModel):
    _name = 'facturae.config'
    _inherit = 'res.config'
    _description = __doc__

    def default_get(self, cr, uid, fields_list=None, context=None):
        if context is None:
            context = {}
        defaults = super(facturae_config, self).default_get(
            cr, uid, fields_list=fields_list, context=context)
        logo = open(addons.get_module_resource(
            'l10n_mx_facturae', 'images', 'piramide_azteca.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def _assign_vat(self, cr, uid, vat, company_id, context=None):
        """
        @param vat : VAT that will be set in the company
        @param company_id : Id from the company that the user works
        """
        if context is None:
            context = {}
        partner_id = self.pool.get('res.company').browse(
            cr, uid, company_id).partner_id.id
        partner_obj = self.pool.get('res.partner')
        if partner_obj.check_vat(cr, uid, [partner_id], context):
            partner_obj.write(cr, uid, partner_id, {
                'vat': vat,
            }, context=context)

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        company_id = self.pool.get('res.users').browse(cr, uid, [uid], context)[0].company_id.partner_id.id
        wiz_data = self.read(cr, uid, ids)
        if wiz_data[0]['vat']:
            self._assign_vat(cr, uid, wiz_data[0]["vat"], company_id, context)

    _columns = {
        'vat': fields.char('VAT', 64, help='Federal Register of Causes'),
        'company_id': fields.many2one('res.company', u'Company',
            help="Select company to assing vat and/or cif"),
    }
