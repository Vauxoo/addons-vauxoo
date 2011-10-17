# -*- encoding: utf-8 -*-
# Author=Moises Lopez moylop260@vauxoo.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import time
from osv import osv
from osv import fields
from tools.translate import _

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns={
        'tracking_id': fields.many2one('stock.tracking', 'Pack', help="Logistical shipping unit: pallet, box, pack ..."),
        'move_id': fields.many2one('stock.move', 'Stock Move'),
    }
account_invoice_line()
