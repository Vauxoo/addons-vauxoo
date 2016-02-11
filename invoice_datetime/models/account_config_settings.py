# coding: utf-8
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
from openerp import fields, models, api
from openerp import SUPERUSER_ID


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    select_date = fields.Selection([
        ('date', 'Date'),
        ('datetime', 'Datetime')],
        string="Default date of invoices",
        help="Select the field you want to displayed in the \
              invoice for the selected company.")

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    def get_default_select_date(self, cr, uid, fields_name, context=None):
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            self._default_company(cr, uid))
        type_show_date = self.pool.get("ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date', context=context)
        return {'select_date': type_show_date}

    # @api.multi
    # def get_default_select_date(self):
    #     key_by_company_id = "acc_invoice.date_invoice_type_" + str(
    #         self.env.user.company_id.id)
    #     type_show_date = self.env["ir.config_parameter"].get_param(
    #         key_by_company_id, default='date')
    #     return {'select_date': type_show_date}

    @api.multi
    def set_default_select_date(self):
        """ set default sale and purchase taxes for products """
        users_obj = self.env['res.users']
        if self.env.user.id != SUPERUSER_ID and not users_obj.has_group(
                'base.group_erp_manager'):
            raise openerp.exceptions.AccessError(
                _("Only administrators can change the settings"))
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            company_id = str(record.company_id and
                             record.company_id.id or
                             self.env.user.company_id.id)
            key_by_company_id = "acc_invoice.date_invoice_type_" + company_id
            config_parameters.set_param(
                key_by_company_id, record.select_date or '')

    @api.onchange('company_id')
    def onchange_company_id(self):
        result = super(AccountConfigSettings, self).onchange_company_id()
        type_date = result.get('value', {})
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            self.env.user.company_id.id)
        type_date['select_date'] = self.env["ir.config_parameter"].get_param(
            key_by_company_id, default='date')
        result.update({'value': type_date})
        return result
