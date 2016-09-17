# coding: utf-8

from openerp import api, models


class SaleOrder(models.Model):

    _name = "sale.order"
    _inherit = ['sale.order', 'default.warehouse']

    @api.multi
    def onchange_partner_id(self, partner_id):
        """Change pricelist depending on user sale team.
        """
        res = super(SaleOrder, self).onchange_partner_id(partner_id)
        res_users_obj = self.env['res.users']
        user_brw = res_users_obj.browse(self._uid)
        sale_team_user = user_brw.default_section_id
        pricelist = sale_team_user.default_sale_pricelist or\
            sale_team_user.pricelist_team_ids and\
            sale_team_user.pricelist_team_ids[0]
        res['value']['pricelist_id'] = pricelist.id if pricelist else False
        return res
