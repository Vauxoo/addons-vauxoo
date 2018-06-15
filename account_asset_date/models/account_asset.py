from odoo import models, fields
from odoo.tools.translate import _


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    date = fields.Date('Start Depreciation Date', required=True,
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                help=_('Depreciation start date'),
                                oldname="purchase_date")
    date_acquisition = fields.Date(help=_('Date acquisition'))
