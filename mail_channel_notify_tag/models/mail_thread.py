from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_allowed_message_params(self):
        """Allow channel_ids to pass through the controller whitelist."""
        return super()._get_allowed_message_params() | {"channel_ids"}

    def message_post(self, *, body="", **kwargs):
        """Extract channel_ids before they reach the parent validation."""
        channel_ids = kwargs.pop("channel_ids", [])
        self = self.with_context(mentioned_channel_ids=channel_ids)
        return super().message_post(body=body, **kwargs)

    def _message_post_after_hook(self, message, msg_values):
        """Repost message to mentioned channels after the message is created."""
        result = super()._message_post_after_hook(message, msg_values)
        channel_ids = self.env.context.get("mentioned_channel_ids")
        if channel_ids:
            self._notify_mentioned_channels(message, channel_ids)
        return result

    def _notify_mentioned_channels(self, message, channel_ids):
        """Repost the message to mentioned channels for Discuss visibility.

        Email notifications to channel members are handled separately by
        mail_followers._get_recipient_data on the source record.
        """
        channels = self.env["discuss.channel"].sudo().browse(channel_ids).exists()
        if not channels:
            return
        template = self.env.ref("mail_channel_notify_tag.mail_channel_message_repost")
        channels.message_post_with_source(
            template,
            render_values={"message": message, "source": self},
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
