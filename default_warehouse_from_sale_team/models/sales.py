# coding: utf-8

from openerp import fields, models


class SaleOrder(models.Model):

    _name = "sale.order"
    _inherit = ['sale.order', 'default.warehouse']


class IrSequence(models.Model):

    _inherit = "ir.sequence"

    section_id = fields.Many2one('crm.team', string='Sale team')
