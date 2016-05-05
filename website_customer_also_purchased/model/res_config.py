# coding: utf-8
from openerp import models, fields


class Website(models.TransientModel):
    _inherit = 'website.config.settings'

    cap_sort = fields.Selection(string='Default Sort',
                                related='website_id.cap_sort')
