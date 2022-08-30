from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _validate_tag_button(self, node, name_manager, node_info):
        """At the moment to install search_action_domain with base_automation, an error
        appears to indicate the created button is not a valid action for base.automation.
        This fix avoid the validation for the created button if base_automation
        installation is in process.
        """
        if name_manager.model._name == "base.automation" and node.get("name") == "create_as_ir_filter":
            node_info.update({"validate": 0})
        return super()._validate_tag_button(node, name_manager, node_info)
