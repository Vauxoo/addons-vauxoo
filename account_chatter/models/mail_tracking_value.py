from odoo import api, models


class MailTrackingValue(models.Model):
    _inherit = "mail.tracking.value"

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):
        """Perform a field tracking over many2many fields of model ``account.account``

        This is performed manually because field tracking over many2many fields is not
        natively supported.
        """
        values = super().create_tracking_values(
            initial_value,
            new_value,
            col_name,
            col_info,
            tracking_sequence,
            model_name,
        )
        if values or model_name != "account.account" or col_info["type"] != "many2many":
            return values
        field = self.env["ir.model.fields"]._get(model_name, col_name)
        if not field:
            return
        old_value_char = ", ".join(initial_value.sudo().mapped("display_name")) if initial_value else ""
        new_value_char = ", ".join(new_value.sudo().mapped("display_name")) if new_value else ""
        return {
            "field": field.id,
            "field_desc": col_info["string"],
            "field_type": col_info["type"],
            "tracking_sequence": tracking_sequence,
            "old_value_char": old_value_char,
            "new_value_char": new_value_char,
        }
