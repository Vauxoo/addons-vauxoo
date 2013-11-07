# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
import os
import time


class res_company(osv.Model):
    _inherit = 'res.company'

    def get_address_invoice_parent_company_id(self, cr, uid, ids, field, arg, context=None):
        if context is None:
            context = {}
        res = {}
        partner_obj = self.pool.get('res.partner')
        companies = self.browse(cr, uid, ids, context=context)
        for company_id in companies:
            partner_parent = company_id and company_id.parent_id and \
                company_id.parent_id.partner_id or False
            if partner_parent:
                address_id = partner_obj.address_get(cr, uid,
                                [partner_parent.id], ['invoice'])['invoice']
            # Validar, si tiene hijos utilizar no utilizar la main, mejor
            # utilizar la normal company_id.partner_id.id
            elif company_id.company_address_main_id:
                address_id = company_id.company_address_main_id.id
            else:
                address_id = partner_obj.address_get(cr, uid,
                            [company_id.partner_id.id], ['invoice'])['invoice']
            res[company_id.id] = address_id
        return res

    _columns = {
        'address_invoice_parent_company_id': fields.many2one("res.partner",
            'Invoice Company Address Parent', help="In this field should \
            placed the address of the parent company , independently if \
            handled a scheme Multi-company o Multi-Address.",
            domain="[('type', '=', 'invoice')]"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
