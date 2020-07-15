# coding: utf-8

from openerp import fields, models, api


class SaleOrder(models.Model):

    _name = "sale.order"
    _inherit = ['sale.order', 'default.warehouse']

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        default_journals = self.team_id.journal_team_ids.filtered(
            lambda x: x.type == 'sale')
        default_journal_id = default_journals[0] if default_journals else False
        if default_journal_id:
            res['journal_id'] = default_journal_id.id
        return res


class IrSequence(models.Model):

    _inherit = "ir.sequence"

    section_id = fields.Many2one('crm.team', string='Sales Team')
