# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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
#

import openerp

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID


class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
        'groups_id': fields.many2one('res.groups', 'Category',),
        'select_date': fields.selection([('date', 'Date'), (
            'datetime', 'Datetime')],
            string="Default date of invoices",
            help="Select the field you want to displayed in the \
                  invoice for the selected company."),
    }

    def get_default_select_date(self, cr, uid, fields_name, context=None):
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            self._default_company(cr, uid))
        type_show_date = self.pool.get("ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date', context=context)
        return {'select_date': type_show_date}

    def set_default_select_date(self, cr, uid, ids, context=None):
        """ set default sale and purchase taxes for products """
        if uid != SUPERUSER_ID and not self.pool['res.users'].has_group(
                cr, uid, 'base.group_erp_manager'):
            raise openerp.exceptions.AccessError(
                _("Only administrators can change the settings"))
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            company_id = str(record.company_id and
                             record.company_id.id or
                             self._default_company(cr, uid))
            key_by_company_id = "acc_invoice.date_invoice_type_" + company_id
            config_parameters.set_param(
                cr, uid, key_by_company_id, record.select_date or '',
                context=context)

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        result = super(account_config_settings, self).onchange_company_id(
            cr, uid, ids, company_id, context=context)
        type_date = False
        type_date = result.get('value', {})
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            company_id or self._default_company(cr, uid))
        type_date['select_date'] = self.pool.get(
            "ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date', context=context)
        result.update({'value': type_date})
        return result
