# -*- coding: utf-8 -*-

from openerp import fields, models


class ResCompany(models.Model):
    """Add field to configure.
    """
    _inherit = 'res.company'

    make_journal_entry = fields.Boolean(
        string='Make journal entry',
        help='Make journal entry in update of cost in products like average')
