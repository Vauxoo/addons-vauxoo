# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class AccountAccount(models.Model):

    _name = "account.account"
    _inherit = ['account.account', 'mail.thread']
    _translate = False

    name = fields.Char(track_visibility=True)
    currency_id = fields.Many2one(track_visibility=True)
    code = fields.Char(track_visibility=True)
    deprecated = fields.Boolean(track_visibility=True)
    reconcile = fields.Boolean(track_visibility=True)
    user_type_id = fields.Many2one(track_visibility=True)
    tax_ids = fields.Many2many(track_visibility=True)
    tag_ids = fields.Many2many(track_visibility=True)
    group_id = fields.Many2one(track_visibility=True)
    realizable_account = fields.Boolean(track_visibility=True)

    """
    Funtion:
        Track changes in tag_ids and tax_ids fields.
        Shows old value ---> new value in every changed record.
    """
    def _message_track(self, tracked_fields, initial):
        changes, tracking_value_ids = super()._message_track(tracked_fields, initial)
        for display_name, display_info in tracked_fields.items():
            if display_name not in ('tag_ids', 'tax_ids'):
                continue
            initial_value = initial[display_name]
            new_value = self[display_name]
            if new_value != initial_value and (new_value or initial_value):
                tracking_sequence = getattr(self._fields[display_name], 'track_sequence', 100)
                initial_value = ", ".join(initial_value.mapped('name')) if initial_value else False
                new_value = ", ".join(new_value.mapped('name')) if new_value else False
                display_info['type'] = 'char'
                tracking = self.env['mail.tracking.value'].create_tracking_values(
                initial_value, new_value, display_name, display_info, tracking_sequence)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])
                changes.add(display_name)
        return changes, tracking_value_ids
