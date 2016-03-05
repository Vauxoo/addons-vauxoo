# coding: utf-8

from openerp import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=False,
        )


class MrpRouting(models.Model):
    """
    For specifying the routings of Work Centers.
    """
    _inherit = 'mrp.routing'
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=False,
        )
