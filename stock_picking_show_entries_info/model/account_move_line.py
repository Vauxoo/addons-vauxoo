# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Ernesto García Meidna (ernesto_gm@vauxoo.com)
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
from openerp.osv import osv
from openerp.tools.translate import _


class StockPicking(osv.Model):
    _inherit = "stock.picking"

    def show_entry_lines(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        res = []
        for picking_brw in self.browse(cr, uid, ids, context=context):
            res += [
                aml_brw.id for move in picking_brw.move_lines if move.aml_ids
                for aml_brw in move.aml_ids]
        return {
            'domain': "[('id','in',\
                [" + ','.join([str(item) for item in res]) + "])]",
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    def show_journal_entries(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        res = []
        for picking_brw in self.browse(cr, uid, ids, context=context):
            res += [
                aml_brw.move_id for move in picking_brw.move_lines
                if move.aml_ids for aml_brw in move.aml_ids]
        return {
            'domain': "[('id','in',\
                [" + ','.join([str(item.id) for item in res]) + "])]",
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
