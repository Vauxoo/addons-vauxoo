# Copyright 2020 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    sale_team_ids = fields.Many2many(
        'crm.team', 'sale_member_rel', 'member_id', 'section_id',
        string="User's sales teams",
        help="This is only an informative field. Go to Sales > Sales >"
        " Sales Teams to edit")

    @api.constrains('sale_team_id')
    def _check_section_id(self):
        """ Can only set the Default Sales team if the user is part o
        """
        for user in self.filtered(
                lambda dat: dat.sale_team_id not in dat.sale_team_ids):
            raise ValidationError(_(
                'You can not set %s sale team as default because the user'
                ' do not belongs to the sale teams.\nPlease go to Sales >'
                ' Settings > Users > Sales Teams if you will like to add this'
                ' user to the sales team') % (user.sale_team_id.name))

    @api.multi
    def write(self, vals):
        """The workers cache is cleared when the `sale_team_ids` field is modified to reflect the changes when the
        following domain is called:
        * `rule_default_warehouse_journal`
        """
        res = super(ResUsers, self).write(vals)
        if vals.get("sale_team_ids"):
            self.clear_caches()
        return res

    @api.multi
    def create(self, values):
        """The workers cache is cleared to reflect the changes when the following domain is called:
        * `rule_default_warehouse_journal`
        """
        res = super(ResUsers, self).create(values)
        if values.get("sale_team_ids"):
            self.clear_caches()
        return res
