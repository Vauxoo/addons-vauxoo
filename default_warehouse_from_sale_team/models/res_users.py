# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


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
        if (self.sale_team_id and
           self.sale_team_id not in self.sale_team_ids):
            raise ValidationError(_(
                'You can not set %s sale team as default because the user'
                ' do not belongs to the sale teams.\nPlease go to Sales >'
                ' Settings > Users > Sales Teams if you will like to add this'
                ' user to the sales team') % (self.sale_team_id.name))
