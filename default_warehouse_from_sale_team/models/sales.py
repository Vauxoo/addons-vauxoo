# coding: utf-8

from openerp import api, models


class SaleOrder(models.Model):

    _name = "sale.order"
    _inherit = ['sale.order', 'default.warehouse']

    def get_pricelist(self, warehouse_id):
        dict = {}
        sale_team = self.env['crm.case.section'].search(
            [('default_warehouse', '=', warehouse_id)], limit=1)
        pricelist_sale_ids = sale_team.pricelist_team_ids.filtered(
            lambda pricelist: pricelist.type == 'sale')
        pricelist = sale_team.default_sale_pricelist or\
            pricelist_sale_ids and pricelist_sale_ids[0]
        if pricelist:
            dict['pricelist_id'] = pricelist.id
            dict['domain'] = {'pricelist_id': [
                ('id', 'in', [
                    pric.id for pric in sale_team.pricelist_team_ids if
                    pric.type == 'sale'])]}
        else:
            dict['domain'] = {
                'pricelist_id':
                [('id', 'in', [pric.id for pric in
                               self.env['product.pricelist'].search(
                                   [('type', '=', 'sale')])])]}
        return dict

    @api.onchange('partner_id')
    @api.depends('warehouse_id')
    def get_pricelist_from_partner_id(self):
        """Change pricelist depending on user sale team. It must consult the
        sale team that has default warehouse the warehouse in sale order
        """
        res = self.onchange_partner_id(self.partner_id.id)
        if type(res) is dict and 'value' in res:
            for field, value in res.get('value').items():
                if hasattr(self, field):
                    setattr(self, field, value)
        pricelist_dict = self.get_pricelist(self.warehouse_id.id)
        if 'pricelist_id' in pricelist_dict:
            self.pricelist_id = pricelist_dict['pricelist_id']
        return {'domain': pricelist_dict['domain']}

    @api.onchange('warehouse_id')
    @api.depends('partner_id')
    def get_pricelist_from_warehouse_id(self):
        """Change pricelist depending on warehouse. It must consult the sale
        team that has default warehouse the warehouse in sale order
        """
        res = self.onchange_warehouse_id(self.warehouse_id.id)
        if type(res) is dict and 'value' in res:
            for field, value in res.get('value').items():
                if hasattr(self, field):
                    setattr(self, field, value)
        pricelist_dict = self.get_pricelist(self.warehouse_id.id)
        if 'pricelist_id' in pricelist_dict:
            self.pricelist_id = pricelist_dict['pricelist_id']
        else:
            self.pricelist_id = self.partner_id.property_product_pricelist.id\
                if self.partner_id else False
        return {'domain': pricelist_dict['domain']}
