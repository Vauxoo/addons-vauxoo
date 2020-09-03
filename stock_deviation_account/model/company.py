from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    gain_inventory_deviation_account_id = fields.Many2one(
        'account.account',
        string='Gain Inventory Deviation Account',
    )
    loss_inventory_deviation_account_id = fields.Many2one(
        'account.account',
        string='Loss Inventory Deviation Account',
    )
