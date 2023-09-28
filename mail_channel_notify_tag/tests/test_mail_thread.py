from odoo.tests import TransactionCase, tagged


@tagged("mail_thread")
class TestMailThread(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env.ref("mail.channel_1")
        cls.partner = cls.env.user.partner_id

    def test_01_message_post(self):
        self.partner.message_post(subject="Test Channel IDs", body="Test Message")
        msg = self.channel.message_ids[0]
        self.assertNotEqual(msg.subject, "Test Channel IDs")
        self.assertNotIn("Test Message", msg.body)
        self.partner.message_post(subject="Test Channel IDs", body="Test Message", channel_ids=self.channel.ids)
        msg = self.channel.message_ids[0]
        self.assertEqual(msg.subject, "Test Channel IDs")
        self.assertIn("Test Message", msg.body)
