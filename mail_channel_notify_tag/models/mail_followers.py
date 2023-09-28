from odoo import models


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None):
        """Inheritance to take into account the partners from the channels to notify them by email"""
        channel_ids = self.env.context.get("mentioned_channel_ids")
        if pids is None:
            pids = set()
        if channel_ids:
            pids |= set(self.env["mail.channel"].sudo().browse(channel_ids).channel_partner_ids.ids)
        return super()._get_recipient_data(records, message_type, subtype_id, pids)
