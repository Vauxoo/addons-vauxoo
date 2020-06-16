from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = 'Companies'

    bank_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Bank Gain Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Bank Gain Exchange Rate Account for booking '
              'Difference'))
    rec_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Receivable Gain Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Receivable Gain Exchange Rate Account for booking '
              'Difference'))
    pay_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Payable Gain Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Payable Gain Exchange Rate Account for booking '
              'Difference'))
    bank_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Bank Loss Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Bank Loss Exchange Rate Account for booking '
              'Difference'))
    rec_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Receivable Loss Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Receivable Loss Exchange Rate Account for booking '
              'Difference'))
    pay_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Payable Loss Account',
        domain=([("user_type_id.type", "!=", "other")]),
        required=False,
        help=('Payable Loss Exchange Rate Account for booking '
              'Difference'))
    journal_id = fields.Many2one(
        'account.journal', 'Posting Journal',
        domain=([('type', '=', 'general')]),
        required=False)
    check_non_multicurrency_account = fields.Boolean(
        'Check Non-Multicurrency Account',
        help="Check Accounts that were not set as multicurrency, "
        "i.e., they were not set with a secondary currency, "
        "but were involved in multicurrency transactions")
