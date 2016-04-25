# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import models, fields, api, _
from openerp import exceptions


class StockTansferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.multi
    def get_chec_inv_pick(self):
        key = "stock.check_inv_pick"
        check_inv_pick = self.env["ir.config_parameter"].get_param(
            key, default=True)
        for record in self:
            record.check_inv_pick = check_inv_pick
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice to validate')
    picking_type_code = fields.Char(
        string='Picking Type Code', related='picking_id.picking_type_code')
    check_inv_pick = fields.Boolean(
        "Check invoice vs picking", compute=get_chec_inv_pick)

    @api.multi
    def do_detailed_transfer(self):
        key = "stock.check_inv_pick"
        check_inv_pick = self.env["ir.config_parameter"].get_param(
            key, default=True)
        if not check_inv_pick:
            res = super(StockTansferDetails, self).do_detailed_transfer()
            return res
        for transfer in self:
            if transfer.picking_type_code == 'outgoing' and \
                    transfer.picking_id.check_invoice:
                invoice = transfer.invoice_id
                old_invoice = self.env['stock.picking'].search(
                    [('picking_type_code', '=', 'outgoing'),
                     ('invoice_id', '=', invoice.id)])
                if old_invoice:
                    msg = _(
                        'You cannot transfer the current picking, '
                        'because the invoice is already registered with the '
                        'picking %s') % (transfer.picking_id.name)
                    raise exceptions.Warning(
                        ('Warning!'), msg)
                tran_dict = {}
                for item in transfer.item_ids:
                    qty = tran_dict.get(item.product_id.id, 0) + item.quantity
                    tran_dict.update({item.product_id.id: qty})
                inv_dict = {}
                for item in invoice.invoice_line.filtered(
                        lambda r: r.product_id.type in ('consu', 'product')):
                    qty = inv_dict.get(item.product_id.id, 0) + item.quantity
                    inv_dict.update({item.product_id.id: qty})
                if inv_dict == tran_dict:
                    transfer.picking_id.invoice_id = invoice.id
                    res = super(
                        StockTansferDetails, self).do_detailed_transfer()
                    return res
                else:
                    raise exceptions.Warning(
                        _('Warning!'),
                        _('Incorrect Invoice, '
                          'products and quantities are different '
                          'between moves and invoice lines.'))
                    # raise exceptions.Warning(
                    #     _('Warning!'), _('Incorrect Invoice'))
            else:
                res = super(StockTansferDetails, self).do_detailed_transfer()
                return res
