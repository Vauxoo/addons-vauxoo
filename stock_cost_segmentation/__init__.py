# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from . import models
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def pre_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['stock.move'].initializing_stock_segmentation()
