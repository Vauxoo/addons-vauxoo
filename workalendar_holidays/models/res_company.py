# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    planned by: Gabriela Quilarque <gabriela@vauxoo.com>
#
############################################################################
from openerp import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    logistic_calendar_id = fields.Many2one(
        'resource.calendar', string="Logistic Work Time",
        domain="[('company_id', '=', id)]",
        help="Company schedule for logistic operations")
