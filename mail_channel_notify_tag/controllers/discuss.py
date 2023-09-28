from odoo.addons.mail.controllers.discuss import DiscussController


class DiscussChannel(DiscussController):
    def _get_allowed_message_post_params(self):
        """composer is passing channel_ids again, it is required to allow it to be available in message_post"""
        return super()._get_allowed_message_post_params() | {"channel_ids"}
