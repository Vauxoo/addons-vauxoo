# coding: utf-8
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2018 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#    Coded by: Edgar Rivero (edgar@vauxoo.com)
############################################################################
from odoo import models, api


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    @api.multi
    def post_inventory_workorder(self):
        for order in self:
            order.production_id.post_inventory()
        return True
