# coding: utf-8

from openerp import models, api


class DefaultPickingType(models.Model):

    _name = 'default.picking.type'
    _inherit = ['default.warehouse']
    _description = "Default Operation Type"

    @api.model
    def default_get(self, fields_list):
        """This  method is added to get by default the picking type depending
        of the sale team warehouse in models where picking type is required
        instead warehouse like purchase order and purchase requisition
        returning the first picking type that match with the warehouse
        of the sale team """
        user_obj = self.env['res.users']
        picking_type_obj = self.env['stock.picking.type']

        res = super(DefaultPickingType, self).default_get(fields_list)
        user_id = user_obj.browse(self._uid)
        sale_team_warehouse_id = user_id.sale_team_id.default_warehouse
        if sale_team_warehouse_id:
            pick_type_id = picking_type_obj.search(
                [('code', '=', 'incoming'),
                 ('warehouse_id', '=', sale_team_warehouse_id.id)], limit=1)
            res.update({'picking_type_id': pick_type_id.id})

        return res


class PurchaseOrder(models.Model):

    _name = 'purchase.order'
    _inherit = ['purchase.order', 'default.picking.type']


class PurchaseRequisition(models.Model):

    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition', 'default.picking.type']
