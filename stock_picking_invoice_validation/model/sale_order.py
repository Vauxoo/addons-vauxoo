# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Hugo Adan, hugo@vauxoo.com
############################################################################

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # field to make an exception invalidation invoice vs picking
    check_invoice = fields.Selection(
        [('check', 'Check'),
         ('no_check', 'No Check')], "Verified Invoice",
        default="no_check")

    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).action_ship_create(
            cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids):
            if order.check_invoice == 'check':
                for pick in order.picking_ids:
                    if pick.picking_type_code == 'outgoing':
                        pick.check_invoice = 'check'
                    else:
                        pick.check_invoice = 'no_check'
        return res
