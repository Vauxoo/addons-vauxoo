from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("login")
class TestLogin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.original_email = "original.email@example.com"
        cls.new_email = "new.email@example.com"
        cls.user = new_test_user(cls.env, login=cls.original_email, context={"no_reset_password": True})
        cls.partner = cls.user.partner_id

    def test_01_restrict_email_edition_internal_user(self):
        """Ensure a partner email cannot be changed if such partner is linked to an internal user"""
        error_msg = "It's not possible to change this contact's email"
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.partner.email = self.new_email

    def test_02_sync_login_and_email(self):
        """If a user login is updated, the partner's email should be updated accordingly"""
        self.assertEqual(self.partner.email, self.original_email)
        self.user.login = self.new_email
        self.assertEqual(self.partner.email, self.new_email)

    def test_03_edit_nonemail_login(self):
        """If the user login is not an email, partner's email shouldn't be updated and should be editable"""
        self.user.login = "nonemail.login"
        self.assertEqual(self.partner.email, self.original_email)
        self.partner.email = self.new_email
        self.assertEqual(self.partner.email, self.new_email)

    def test_04_edit_email_case_insensitive(self):
        """Editing a partner's email should be allowed if only the letter casing is being changed"""
        self.user.login = self.new_email.upper()
        self.assertEqual(self.partner.email, self.new_email.upper())
        self.partner.email = self.new_email
        self.partner.email = self.new_email.title()
        error_msg = "It's not possible to change this contact's email"
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.partner.email = self.original_email
