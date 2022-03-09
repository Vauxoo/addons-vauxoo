from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    sale_team_ids = fields.Many2many(
        "crm.team", "sale_member_rel", "member_id", "section_id",
        string="Allowed sales teams",
        help="Sales teams allowed for the user, to give access to warehouses and their related documents.",
    )

    @api.constrains('sale_team_id')
    def _check_section_id(self):
        """ Can only set the Default Sales team if the user has that team on its
        Sales Teams (`sale_team_ids`).
        """
        user_wrong_team = self.filtered(lambda u: u.sale_team_id - u.sale_team_ids)
        if user_wrong_team:
            raise ValidationError(_(
                "The chosen team (%s) is not in the allowed sales teams for this user",
                user_wrong_team[0].sale_team_id.name
            ))

    def _get_default_warehouse_id(self):
        """Take the warehouse set in sales team as default one, otherwise fallback on user's one"""
        return (
            self.env.user.sale_team_id.default_warehouse_id
            or super()._get_default_warehouse_id()
        )
