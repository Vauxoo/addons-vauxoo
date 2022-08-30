from odoo.tests import Form, TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("models")
class TestModels(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env.ref("base.model_res_partner")

    def create_server_action(self, code=""):
        search_action = Form(self.env["ir.actions.server"])
        search_action.name = "TEST: test"
        search_action.model_id = self.partner_model
        search_action.state = "code"
        search_action.code = code
        search_action = search_action.save()
        return search_action

    def test_01_search_action_domain(self):
        # Create the server action
        search_action = self.create_server_action(
            code="""
elements = env['res.partner'].search([('is_company', '=', True)])
action = {'domain': [('id', 'in', elements.ids)]}
            """
        )
        # Execute "Create As Filter" method from the created server action
        search_action.create_as_ir_filter()
        # Check if the filter was created successfully
        created_filter = self.env.ref(
            "search_action_domain.ir_filters_server_action_%s" % search_action.id,
            raise_if_not_found=False,
        )
        self.assertTrue(created_filter)
        self.assertEqual(created_filter.name, search_action.name)
        # Apply the filter succesfully
        ctx = safe_eval(created_filter.context)
        found_partner_action = self.env["res.partner"].with_context(**ctx).search([])
        found_partner_search = self.env["res.partner"].search([("is_company", "=", True)])
        self.assertEqual(found_partner_action, found_partner_search)
