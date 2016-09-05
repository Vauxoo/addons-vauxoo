# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Compute segmentation_cost field"""
    context = {'force_segmentation_cost': True}
    env = api.Environment(cr, SUPERUSER_ID, context)
    env['stock.quant'].search([]).write({})
