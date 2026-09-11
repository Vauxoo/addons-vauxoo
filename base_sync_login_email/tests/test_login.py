from odoo import Command
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

    def test_05_data_files_bypass_constraint(self):
        """Records loaded from data/demo files must be free to desync email and login, otherwise installing a
        module that ships such users fails (Odoo's own payroll demo does exactly that)"""
        self.partner.with_context(install_mode=True).email = self.new_email
        self.assertEqual(self.partner.email, self.new_email)
        # Creating a user on a partner whose email does not match the login is the exact pattern used by
        # Odoo's payroll demo files, so it must succeed as well
        demo_partner = self.env["res.partner"].create({"name": "Demo Partner", "email": "demo.partner@example.com"})
        demo_user = (
            self.env["res.users"]
            .with_context(no_reset_password=True, install_mode=True)
            .create(
                {
                    "name": "Demo User",
                    "login": "demo.user@example.com",
                    "partner_id": demo_partner.id,
                    "group_ids": [Command.set([self.env.ref("base.group_user").id])],
                }
            )
        )
        self.assertEqual(demo_user.partner_id, demo_partner)
        self.assertEqual(demo_partner.email, "demo.partner@example.com")
        # Outside data loading the safeguard keeps working on that same partner
        error_msg = "It's not possible to change this contact's email"
        with self.assertRaisesRegex(ValidationError, error_msg):
            demo_partner.email = "another.email@example.com"
