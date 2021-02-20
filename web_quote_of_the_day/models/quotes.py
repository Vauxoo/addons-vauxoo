# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
class Quotes(models.Model):
    _name = 'quote'
    _description = 'Quotes'

    quote = fields.Char()
    background = fields.Binary()
    author = fields.Char()
    last_date_shown = fields.Datetime()
