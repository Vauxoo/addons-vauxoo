from openerp import fields, models


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    section_id = fields.Many2one('crm.team', string='Sales Team')
