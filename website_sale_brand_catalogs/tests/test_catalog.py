from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCatalog(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_email = "test@test.com"

    def test_01_lead(self):
        self.start_tour("/", "website_sale_brand_catalogs.test_catalog", login=None)
        lead_email = self.env["crm.lead"].search([("email_from", "=", "test@test.com")], limit=1)
        self.assertEqual(lead_email.email_from, self.test_email)
