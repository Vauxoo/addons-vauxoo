from odoo import models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    def create_as_ir_filter(self):
        self.env["ir.filters"]._load_records(
            [
                {
                    "xml_id": "search_action_domain.ir_filters_server_action_%s" % record.id,
                    "noupdate": True,
                    "values": {
                        "name": record.name,
                        "model_id": record.model_id.model,
                        "context": "{'search_action_domain': {'%s': [%s]}}" % (record.model_id.model, record.id),
                        "user_id": False,
                        "action_id": False,
                    },
                }
                for record in self.filtered(lambda r: r.state == "code")
            ]
        )
