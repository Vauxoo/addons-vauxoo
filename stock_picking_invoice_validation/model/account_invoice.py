# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Hugo Adan, hugo@vauxoo.com
############################################################################

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(AccountInvoice, self).name_search(
            name, args, operator, limit)
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('number', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('number', operator, name)] + args, limit=limit)
        if recs:
            res = recs.name_get()
        return res
