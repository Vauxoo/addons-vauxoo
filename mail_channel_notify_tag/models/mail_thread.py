from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_channels_from_messages(self, message, **kwargs):
        channel_ids = self.env.context.get("mentioned_channel_ids")
        if not channel_ids:
            return
        kwargs.pop("partner_ids", [])  # Remove target partners to not send duplicate messages.
        subtype_xmlid = kwargs.pop("subtype_xmlid", None)
        if subtype_xmlid:
            kwargs["subtype_id"] = self.env.ref(subtype_xmlid).id
        template = self.env.ref("mail_channel_notify_tag.mail_channel_message_repost")
        values = {"message": message, "source": self}
        self.env["mail.channel"].sudo().browse(channel_ids).message_post_with_view(template, values=values, **kwargs)

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *, body="", **kwargs):
        self = self.with_context(mentioned_channel_ids=kwargs.pop("channel_ids", []))
        message = super().message_post(body=body, **kwargs)
        self._notify_channels_from_messages(message, **kwargs)
        return message
