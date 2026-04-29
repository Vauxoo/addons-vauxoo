from odoo import models


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None):
        """Add channel members as email recipients when channels are mentioned."""
        channel_ids = self.env.context.get("mentioned_channel_ids")
        if not channel_ids:
            return super()._get_recipient_data(records, message_type, subtype_id, pids)
        pids = set(pids) if pids else set()
        pids |= set(self.env["discuss.channel"].sudo().browse(channel_ids).channel_partner_ids.ids)
        return super()._get_recipient_data(records, message_type, subtype_id, pids)
