# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: jorge_nr@vauxoo.com
#    planned by: Humberto Arocha <hbto@vauxoo.com>
############################################################################

from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    @api.model
    def _get_policies(self):
        """This is the method to be inherited for adding policies"""
        return [('optional', _('Optional')),
                ('always', _('Always')),
                ('never', _('Never'))]

    asset_policy = fields.Selection(
        _get_policies, 'Policy for asset category', required=True,
        help="Set the policy for the asset category field : if you select "
        "'Optional', the accountant is free to put a asset category on an "
        "account invoice line with this type of account; if you select "
        "'Always', the accountant will get an error message if there is no "
        "asset category; if you select 'Never', the accountant will get an "
        "error message if a asset category is present.", default='optional')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _get_asset_category_policy(self, account):
        """ Extension point to obtain analytic policy for an account """
        return account.user_type_id.asset_policy

    @api.multi
    def _check_asset_category_required(self):
        for line in self:
            policy = self._get_asset_category_policy(line.account_id)
            if policy == 'always' and not line.asset_category_id:
                raise ValidationError(_(
                    "Asset policy is set to 'Always' for the account '%s %s' "
                    "but the asset category is missing in the account invoice "
                    "line with description '%s'.") % (
                        line.account_id.code, line.account_id.name,
                        line.name))
            elif policy == 'never' and line.asset_category_id:
                raise ValidationError(_(
                    "Asset policy is set to 'Never' for the account '%s %s' "
                    "but the invoice line with description '%s' have this "
                    "asset category set: '%s'.")
                    % (line.account_id.code, line.account_id.name, line.name,
                       line.asset_category_id.name))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice.invoice_line_ids._check_asset_category_required()
        return res
