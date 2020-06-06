from odoo import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_start(self):
        """NOTE: This method is a copy of the original one in odoo named action_done but we add
        a new section of code to introduce exception on the test.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        if not self._context.get('allow_past_date_quants'):
            return super(StockInventory, self).action_start()

        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            # NOTE VX: This section was overwritten.
            vals = {'state': 'confirm', 'date': inventory.date or fields.Datetime.now()}
            # NOTE VX: End of overwrite
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [
                    (0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(StockInventoryLine, self)._get_move_values(qty, location_id, location_dest_id, out)
        if self._context.get('allow_past_date_quants'):
            res['move_line_ids'][0][2]['date'] = self.inventory_id.date
        return res
