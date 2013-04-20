#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
from openerp.tools.translate import _

from openerp.osv import osv, fields
import decimal_precision as dp


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'quantity': fields.float('Quantity',
             digits_compute=dp.get_precision(
                 'Product UoM'),
             help="The optional quantity expressed by this line,\
             eg: number of product sold. The quantity is not a legal\
             requirement but is very useful for some reports."),
    }
