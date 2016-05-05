# coding: utf-8
from openerp import models, fields


class Website(models.Model):
    _inherit = 'website'

    cap_sort = fields.Selection(
        [('best_seller', 'Best Seller')], defult="best_seller")
