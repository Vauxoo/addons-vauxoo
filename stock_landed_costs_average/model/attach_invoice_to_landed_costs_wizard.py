# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.osv import osv


class AttachInvoiceToLandedCostsWizard(models.TransientModel):
    _name = 'attach.invoice.to.landed.costs.wizard'
    stock_landed_cost_id = fields.Many2one(
        'stock.landed.cost',
        string='Landed Costs',
        )

    @api.multi
    def add_landed_costs(self):
        """ Attach an invoice to a Landed Costs object.
        Note: Only applies to one invoice at time """
        ai_obj = self.env['account.invoice']

        ctx = dict(self._context)
        ai_brw = ai_obj.browse(ctx['active_id'])
        state = ai_brw.stock_landed_cost_id and \
            ai_brw.stock_landed_cost_id.state or 'draft'
        if state == 'done':
            raise osv.except_osv(
                _('Invalid Procedure'),
                _('You cannot change to another Landed Costs as the one your '
                  'Invoice is linked is not in Draft State!'))
        ai_brw.write(
            {'stock_landed_cost_id': self.stock_landed_cost_id.id})
        return True
