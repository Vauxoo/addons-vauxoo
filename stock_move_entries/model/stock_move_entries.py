# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
#              Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, _, api
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    """
    """

    sm_id = fields.Many2one('stock.move', 'Stock move')


class StockMove(models.Model):
    _inherit = "stock.move"

    """
    """

    aml_ids = fields.One2many(
        'account.move.line', 'sm_id', 'Account move Lines',
        domain=[('account_id.reconcile', '=', True)])
    aml_all_ids = fields.One2many(
        'account.move.line', 'sm_id', 'All Account move Lines')

    def _prepare_account_move_line(self, qty, cost, credit_account_id,
                                   debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)
        for line in res:
            line[2]['sm_id'] = self.id
        return res


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def show_entry_lines(self):
        move_line_ids = self.env['account.move.line']._search(
            [('sm_id', 'in', self.mapped('move_lines').ids)])
        if not move_line_ids:
            raise UserError(
                _('Warning !\nThere is no Journal Items '
                  'related with the picking'))
        return {
            'domain': [('id', 'in', move_line_ids)],
            'name': _('Related Journal Items'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            }

    @api.multi
    def show_journal_entries(self):
        move_line_ids = self.env['account.move.line'].search(
            [('sm_id', 'in', self.mapped('move_lines').ids)])
        move_ids = move_line_ids.mapped('move_id').ids
        if not move_ids:
            raise UserError(
                _('Warning !\nThere is no Journal Entries '
                  'related with the picking'))
        return {
            'domain': [('id', 'in', move_ids)],
            'name': _('Related Journal Entries'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            }
