# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class AccountAccount(models.Model):

    _name = "account.account"
    _inherit = ['account.account', 'mail.thread']

    name = fields.Char(tracking=True)
    currency_id = fields.Many2one(tracking=True)
    code = fields.Char(tracking=True)
    deprecated = fields.Boolean(tracking=True)
    reconcile = fields.Boolean(tracking=True)
    user_type_id = fields.Many2one(tracking=True)
    tax_ids = fields.Many2many(tracking=True)
    tag_ids = fields.Many2many(tracking=True)
    group_id = fields.Many2one(tracking=True)

    def _message_track(self, tracked_fields, initial):
        """Perform a field tracking over tax_ids and tag_ids

        This is performed manually because field tracking over many2many fields is not
        natively supported.
        """
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
