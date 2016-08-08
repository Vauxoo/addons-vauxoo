# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = "res.users"

    sale_team_ids = fields.Many2many(
        'crm.case.section', 'sale_member_rel', 'member_id', 'section_id',
        string="User's sales teams",
        help="This is only an informative field. Go to Sales > Sales >"
        " Sales Teams to edit")

    @api.constrains('default_section_id')
    def _check_section_id(self):
        """ Can only set the Default Sales team if the user is part o
        """
        if self.default_section_id and \
           self.default_section_id not in self.sale_team_ids:
            raise ValidationError(_(
                'You can not set %s sale team as default because the user'
                ' do not belongs to the sale teams.\nPlease go to Sales >'
                ' Sales > Sales Teams menu if you will like to add this'
                ' user to the sales team') % (self.default_section_id.name))
