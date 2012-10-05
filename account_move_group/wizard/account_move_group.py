# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
import time
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class account_move_group(osv.osv_memory):
    _name='account.move.group'
    
    def move_group(self, cr, uid, ids, context=None):
        account_move = self.pool.get('account.move')
        account_move_line = self.pool.get('account.move.line')
        if context is None:
            context = {}
        move_ids = context.get('active_ids', [])
        res_journal = {}
        res_period = {}
        res_reference = {}
        moves = []
        moves_line = []
        for move in account_move.browse(cr, uid, move_ids, context=context):
            moves.append(move.id)
            for mov in move.line_id:
                res_reference.setdefault(move.ref, 0)
                res_journal.setdefault(mov.journal_id.id, 0)
                res_period.setdefault(mov.period_id.id, 0)
                moves.append(mov.id)
        if len(moves) <= 1:
            raise osv.except_osv(_('Error'), _('You need at least two entries to merged') )
        if len(res_journal) > 1 or len(res_journal) > 1:
            raise osv.except_osv(_('Error'), _('Entries can not merge') )
        else:
            reference = ','.join(lin for lin in res_reference.keys())
            move_id = account_move.create(cr, uid, {
                        'journal_id': res_journal.keys()[0],
                        'ref': reference
                        })
            account_move_line.write(cr, uid, moves_line, {'move_id':move_id})
            account_move.unlink(cr, uid, move_ids)
        return {}
    
account_move_group()


















