from odoo.tests import TransactionCase, tagged


@tagged("mail_thread")
class TestMailThread(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.member_user = (
            cls.env["res.users"]
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Channel Member",
                    "login": "channel_member_test",
                    "email": "member@test.com",
                    "notification_type": "email",
                }
            )
        )
        cls.member_partner = cls.member_user.partner_id
        cls.channel = cls.env["discuss.channel"].create(
            {
                "name": "Test Notify Channel",
                "channel_type": "channel",
            }
        )
        cls.channel.add_members(partner_ids=cls.member_partner.ids)
        cls.partner = cls.env.user.partner_id

    def test_01_message_post_without_channel_ids(self):
        """Messages without channel_ids should not appear in the channel."""
        initial_count = len(self.channel.message_ids)
        self.partner.message_post(subject="No Channel", body="No repost expected")
        self.assertEqual(len(self.channel.message_ids), initial_count)

    def test_02_message_post_with_channel_ids(self):
        """Messages with channel_ids should be reposted to the mentioned channel."""
        self.partner.message_post(
            subject="Test Channel IDs",
            body="Test Message",
            channel_ids=self.channel.ids,
        )
        msg = self.channel.message_ids[0]
        self.assertIn("Test Message", msg.body)

    def test_03_email_notification_queued(self):
        """Channel members with email preference should get a queued mail.mail."""
        self.partner.message_post(
            subject="Email Test",
            body="Email Notification",
            channel_ids=self.channel.ids,
        )
        mail = self.env["mail.mail"].search([("recipient_ids", "in", self.member_partner.ids)])
        self.assertTrue(mail, "Email notification should be queued for channel member")
