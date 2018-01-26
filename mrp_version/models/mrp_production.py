# coding: utf-8
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2018 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#    Coded by: Edgar Rivero (edgar@vauxoo.com)
############################################################################
from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    backorder_id = fields.Many2one(
        'mrp.production', string="Back Order Production",
        help="""When a production order is canceled with the wizard to
        change the route, in this field it will store the order from
        where it comes.""")
