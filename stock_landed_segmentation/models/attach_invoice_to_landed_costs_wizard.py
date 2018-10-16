# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AttachInvoiceToLandedCostsWizard(models.TransientModel):
    _name = 'attach.invoice.to.landed.costs.wizard'

    stock_landed_cost_id = fields.Many2one(
        'stock.landed.cost',
        string='Landed Costs',
    )

    @api.multi
    def add_landed_costs(self):
        """Attach an invoice to a Landed Costs object.
        Note: Only applies to one invoice at time
        """
        ai_obj = self.env['account.invoice']

        ctx = dict(self._context)
        ai_brw = ai_obj.browse(ctx['active_id'])
        old_slc_brw = ai_brw.stock_landed_cost_id
        old_state = old_slc_brw.state or 'draft'
        if old_state == 'done':
            raise UserError(
                _('You cannot change to another Landed Costs as the one your '
                  'Invoice is linked to (Old One) is not in Draft State!'))

        new_state = self.stock_landed_cost_id.state or 'draft'
        if new_state == 'done':
            raise UserError(
                _('You cannot change to another Landed Costs as the one you '
                  'are try to link to (New One) is not in Draft State!'))

        ai_brw.write(
            {'stock_landed_cost_id': self.stock_landed_cost_id.id})
        self.stock_landed_cost_id.get_costs_from_invoices()
        old_slc_brw.get_costs_from_invoices()
        return True
