# coding: utf-8

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    code = fields.Char(help="Internal code name of the company")

    @api.constrains('code')
    def unique_code(self):
        for record in self:
            if record.code and record.search(
                    [('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError(_('Code must be unique'))
