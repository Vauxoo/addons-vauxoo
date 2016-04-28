# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Hugo Adan, hugo@vauxoo.com
############################################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _get_company_conf(self):
        check_inv_pick = self.env.user.company_id.check_invoice
        return check_inv_pick

    # field to make an exception invalidation invoice vs picking
    check_invoice = fields.Boolean(
        "Verified Invoice", default=_get_company_conf)

    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(SaleOrder, self).action_ship_create(
            cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids):
            if order.check_invoice:
                for pick in order.picking_ids:
                    pick.check_invoice = pick.picking_type_code == 'outgoing'
        return res
