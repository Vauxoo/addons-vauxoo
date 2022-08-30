from odoo import fields, models


class AccountAnalytic(models.Model):
    _inherit = "account.analytic.account"

    business_unit_id = fields.Many2one("account.analytic.business.unit")

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            if analytic.business_unit_id:
                name = "BU: " + analytic.business_unit_id.code
            if analytic.code:
                name = "[" + analytic.code + "] " + name
            if analytic.partner_id.commercial_partner_id.name:
                name = name + " - " + analytic.partner_id.commercial_partner_id.name
            res.append((analytic.id, name))
        return res
