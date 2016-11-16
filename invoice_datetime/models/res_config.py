# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo (Moises Lopez <moylop260@vauxoo.com>
#                        Osval Reyes <osval@vauxoo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, exceptions, fields, models, SUPERUSER_ID


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    groups_id = fields.Many2one('res.groups', 'Category',)
    select_date = fields.Selection([
        ('date', 'Date'),
        ('datetime', 'Datetime')],
        string="Default date of invoices",
        help="Select the field you want to displayed in the "
        "invoice for the selected company.")

    @api.model
    def _default_company(self):
        return self.env.user.company_id.id

    @api.model
    def default_get(self, fields):
        res = super(AccountConfigSettings, self).default_get(fields)
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            self._default_company())
        type_show_date = self.env["ir.config_parameter"].get_param(
            key_by_company_id, default='date')
        res.update({
            'select_date': type_show_date
        })
        return res

    @api.multi
    def set_default_select_date(self):
        """Set default sale and purchase taxes for products"""
        if self.env.user.id != SUPERUSER_ID and not self.env.user.\
                has_group('base.group_erp_manager'):
            raise exceptions.AccessError(
                _("Only administrators can change the settings"))
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            company_id = str(record.company_id and record.company_id.id or
                             self._default_company())
            key_by_company_id = "acc_invoice.date_invoice_type_" + company_id
            config_parameters.set_param(
                key_by_company_id, record.select_date or '')

    def onchange_company_id(self, company_id):
        result = super(AccountConfigSettings, self).onchange_company_id(
            company_id)
        type_date = result.get('value', {})
        key_by_company_id = "acc_invoice.date_invoice_type_" + str(
            company_id or self._default_company())
        type_date['select_date'] = self.env["ir.config_parameter"].get_param(
            key_by_company_id, default='date')
        result.update({'value': type_date})
        return result
