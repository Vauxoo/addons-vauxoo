# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: jorge_nr@vauxoo.com
#    planned by: Humberto Arocha <hbto@vauxoo.com>
############################################################################

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class account_account_type(orm.Model):
    _inherit = "account.account.type"

    def _get_policies(self, cr, uid, context=None):
        """This is the method to be inherited for adding policies"""
        return [('optional', _('Optional')),
                ('always', _('Always')),
                ('never', _('Never'))]

    _columns = {
        'asset_policy': fields.selection([
            ('optional', 'Optional'),
            ('always', 'Always'),
            ('never', 'Never')
            ],
            'Policy for asset category',
            required=True,
            help="Set the policy for the asset category field : if you select "
                 "'Optional', the accountant is free to put a asset category "
                 "on an account invoice line with this type of account ; "
                 "if you select 'Always', the accountant will get an error "
                 "message if there is no asset category ; "
                 "if you select 'Never', the accountant will get an "
                 "error message if a asset category is present."),
    }

    _defaults = {
        'asset_policy': lambda *a: 'optional',
    }


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def _get_asset_category_policy(self, cr, uid, account, context=None):
        """ Extension point to obtain analytic policy for an account """
        return account.user_type.asset_policy

    def _check_asset_category_required_msg(self, cr, uid, ids, context=None):
        for account_move_line in self.browse(cr, SUPERUSER_ID, ids, context):

            policy = self._get_asset_category_policy(
                cr, uid, account_move_line.account_id, context=context)
            if policy == 'always' and not account_move_line.asset_category_id:
                return _("Asset policy is set to 'Always' "
                         "with account %s '%s' but the "
                         "asset category is missing in the account "
                         "invoice line with description is '%s'." %
                         (account_move_line.account_id.code,
                          account_move_line.account_id.name,
                          account_move_line.name))
            elif policy == 'never' and account_move_line.asset_category_id:
                return _("Asset policy is set to 'Never' "
                         "with account %s '%s' but the "
                         "account invoice line with description is '%s' " %
                         (account_move_line.account_id.code,
                          account_move_line.account_id.name,
                          account_move_line.name))

    def _check_asset_category_required(self, cr, uid, ids, context=None):
        return not self._check_asset_category_required_msg(
            cr, uid, ids, context=context)

    _constraints = [
        (_check_asset_category_required,
         _check_asset_category_required_msg,
         ['account_id']),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
