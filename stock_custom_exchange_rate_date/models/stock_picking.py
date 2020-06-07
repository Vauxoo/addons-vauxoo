from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    exchange_rate_date = fields.Date(
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        copy=False,
        help="If set, specifies a customized date that will be used when "
        "computing product unit prices, instead of the date when the transfer "
        "is validated, in case exchange rates are involved.")
