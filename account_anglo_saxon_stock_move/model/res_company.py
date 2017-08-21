# -*- coding: utf-8 -*-

from openerp import fields, models


class ResCompany(models.Model):
    """Add field to configure.
    """
    _inherit = 'res.company'

    writeoff = fields.Boolean(
        string='Reconcile Accruals with write-off',
        help='Reconcile Accruals on Sale/Purchase Order with write-off')
    do_partial = fields.Boolean(
        string='Partially Reconcile Accruals',
        help='Lines will partially reconcile otherwise they will remain loose')
    accrual_offset = fields.Float(
        string='Accrual Offset on Reconciliation',
        help='Threshold used when trying to fully reconcile Accruals')
