#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javier@vauxoo.com
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    '''
    Check that the entry balance is greater than zero
    '''
    def _update_check_nonzero(self, cr, uid, ids, context=None):
        writeoff = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            writeoff = abs(line.debit - line.credit)
            if writeoff == 0.0:
                return False
        return True

    _constraints = [
        (_update_check_nonzero,
         'You can not create an entry with zero balance !\
         Please set amount !', []),
    ]
