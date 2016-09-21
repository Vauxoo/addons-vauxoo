# coding: utf-8

from openerp import models, api


class DefaultPickingType(models.Model):

    _name = 'default.picking.type'

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
        sale_team_warehouse_id = user_id.default_section_id.default_warehouse
        if sale_team_warehouse_id:
            pick_type_id = picking_type_obj.search(
                [('code', '=', 'incoming'),
                 ('warehouse_id', '=', sale_team_warehouse_id.id)], limit=1)
            res.update({'picking_type_id': pick_type_id.id})

        return res


class PurchaseOrder(models.Model):

    _name = 'purchase.order'
    _inherit = ['purchase.order', 'default.picking.type']

    def get_pricelist(self, picking_type_id):
        dict = {}
        picking_type_obj = self.env['stock.picking.type']
        warehouse_id = picking_type_obj.browse(picking_type_id).warehouse_id.id
        sale_team = self.env['crm.case.section'].search(
            [('default_warehouse', '=', warehouse_id)], limit=1)
        pricelist_purchase_ids = sale_team.pricelist_team_ids.filtered(
            lambda pricelist: pricelist.type == 'purchase')
        pricelist = sale_team.default_purchase_pricelist or\
            pricelist_purchase_ids and pricelist_purchase_ids[0]
        if pricelist:
            dict['pricelist_id'] = pricelist.id
            dict['domain'] = {'pricelist_id': [
                ('id', 'in', [
                    pric.id for pric in sale_team.pricelist_team_ids if
                    pric.type == 'purchase'])]}
        else:
            dict['domain'] = {
                'pricelist_id':
                [('id', 'in', [pric.id for pric in
                               self.env['product.pricelist'].search(
                                   [('type', '=', 'purchase')])])]}
        return dict

    @api.onchange('partner_id')
    @api.depends('picking_type_id')
    def get_pricelist_from_partner_id(self):
        """Change pricelist depending on user sale team. It must consult the
        sale team that has default warehouse the warehouse in picking_type_id.
        """
        res = self.onchange_partner_id(self.partner_id.id)
        if type(res) is dict and 'value' in res:
            for field, value in res.get('value').items():
                if hasattr(self, field):
                    setattr(self, field, value)
        pricelist_dict = self.get_pricelist(self.picking_type_id.id)
        if 'pricelist_id' in pricelist_dict:
            self.pricelist_id = pricelist_dict['pricelist_id']
        return {'domain': pricelist_dict['domain']}

    @api.onchange('picking_type_id')
    @api.depends('partner_id')
    def get_pricelist_from_picking_type_id(self):
        """Change pricelist depending on warehouse in picking_type_id.
        It must consult the sale team that has default warehouse
        the warehouse in purchase order
        """
        res = self.onchange_picking_type_id(self.picking_type_id.id)
        if type(res) is dict and 'value' in res:
            for field, value in res.get('value').items():
                if hasattr(self, field):
                    setattr(self, field, value)
        pricelist_dict = self.get_pricelist(self.picking_type_id.id)
        if 'pricelist_id' in pricelist_dict:
            self.pricelist_id = pricelist_dict['pricelist_id']
        else:
            self.pricelist_id = self.partner_id.property_product_pricelist.id\
                if self.partner_id else False
        return {'domain': pricelist_dict['domain']}

class PurchaseRequisition(models.Model):

    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition', 'default.picking.type']
