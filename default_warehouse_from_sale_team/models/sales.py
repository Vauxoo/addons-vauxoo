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
        return dict

    @api.onchange("partner_id", "warehouse_id")
    def onchange_to_get_pricelist(self):
        pricelist_dict = self.get_pricelist(self.warehouse_id)
        if pricelist_dict:
            self.pricelist_id = pricelist_dict['pricelist_id']

    @api.multi
    def onchange_warehouse_id(self, warehouse_id):
        """Change pricelist depending on warehouse. It must consult the sale
        team that has default warehouse the warehouse in sale order"""
        res = super(SaleOrder, self).onchange_warehouse_id(warehouse_id)
        pricelist_dict = self.get_pricelist(warehouse_id)
        if pricelist_dict:
            res['value']['pricelist_id'] = pricelist_dict['pricelist_id']
            res['domain'] = pricelist_dict['domain']
        return res
