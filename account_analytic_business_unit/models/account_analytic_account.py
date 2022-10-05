from odoo import fields, models


class AccountAnalytic(models.Model):
    _inherit = "account.analytic.account"
    _order = "business_unit_id desc, sequence asc, code, name asc"

    business_unit_id = fields.Many2one("account.analytic.business.unit")
    sequence = fields.Integer()

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            bu_prefix = ""
            if analytic.business_unit_id:
                bu_prefix = analytic.business_unit_id.code + ":"
                name = bu_prefix + analytic.name
            if analytic.code:
                name = bu_prefix + ":" + analytic.code + " - " + analytic.name
            if analytic.partner_id.commercial_partner_id.name:
                name = name + " - " + analytic.partner_id.commercial_partner_id.name
            res.append((analytic.id, name))
        return res
