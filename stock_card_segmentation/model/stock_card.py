# coding: utf-8

from openerp import models

# TODO: multi-company awareness to be developed


class StockCardProduct(models.TransientModel):
    _inherit = 'stock.card.product'


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
