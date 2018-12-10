# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _generate_customs_information(self):
        """Search custom information in move type out"""
        if self.env.context.get('origin_move'):
            return super(AccountInvoice, self)._generate_customs_information()
        landed_obj = self.env['stock.landed.cost']
        for line in self.mapped('invoice_line_ids').filtered('sale_line_ids'):
            moves = line.mapped('sale_line_ids.move_ids').filtered(
                lambda r: r.state == 'done' and not r.scrapped)
            landed = moves._get_landed_information()
            if not moves or not landed:
                continue
            line.l10n_mx_edi_customs_number = ','.join(
                list(set(landed.mapped('l10n_mx_edi_customs_number'))))
