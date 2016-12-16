# -*- coding: utf-8 -*-

import logging
from psycopg2 import OperationalError
from openerp import models, api, fields
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    date_stock_card_border = fields.Datetime(string='Stock Card Border Date')

    @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        scp_obj = self.env['stock.card.product']
        scp_brw = scp_obj.create({'product_id': self._ids})
        return scp_brw.stock_card_move_get()

    @api.multi
    def set_stock_card_border_date(self, date_start, date_stop):
        self.ensure_one()
        fnc = self.env['stock.card.product']._stock_card_move_get
        flag = False
        for line in fnc(self.id).get('res'):
            if (line['date'] >= date_start and line['date'] <= date_stop and
                    line['product_qty'] and flag):
                self.sudo().write({'date_stock_card_border': line['date']})
                try:
                    self._cr.commit()
                    _logger.info('Updated Product: [%s]', str(self.id))
                except OperationalError:
                    self._cr.rollback()
                    _logger.info(
                        'Update failed at Product: [%s]', str(self.id))
                break
            elif (line['date'] >= date_start and line['date'] <= date_stop and
                    not line['product_qty'] and not flag):
                flag = True
        return True

    def generate_stock_card_border_conditions(self, date_start, date_stop):
        for prod_brw in self.search(
                [('cost_method', '=', 'average'),
                 ('valuation', '=', 'real_time'),
                 ('date_stock_card_border', '=', False)]):
            prod_brw.set_stock_card_border_date(date_start, date_stop)
        return True
