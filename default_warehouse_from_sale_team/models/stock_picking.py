from odoo import api, fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["default.warehouse.mixin", "stock.picking"]

    warehouse_id = fields.Many2one(related="picking_type_id.warehouse_id")
    is_editable = fields.Boolean(compute="_compute_is_editable")

    @api.depends_context("uid")
    def _compute_is_editable(self):
        # Using intersection operator to keep original env
        editable_records = self & self._filter_access_rules_python("write")
        editable_records.is_editable = True
        (self - editable_records).is_editable = False

    @api.depends("is_editable")
    def _compute_show_check_availability(self):
        res = super()._compute_show_check_availability()
        non_editable = self - self.filtered("is_editable")
        non_editable.show_check_availability = False
        return res
