# coding: utf-8

from odoo import models, fields


class MrpRouting(models.Model):
    """For specifying the routings of Work Centers.
    """
    _inherit = 'mrp.routing'
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=False,
    )
