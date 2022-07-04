
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    hide_totals_at_closing_session = fields.Boolean(help="""If this field is checked, the totals are going to be
 hidden in the closing control pop up, when closing a session. Also, the check box for "Accept payments
 difference and post a profit/loss journal entry" will be automatically hidden and checked.""")
