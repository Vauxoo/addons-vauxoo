# -*- encoding: utf-8 -*-
# Author=Nhomar Hernandez nhomar@vauxoo.com
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


class stock_production_lot(osv.osv):
    _inherit = "stock.tracking"
    _columns={
        'import_id':fields.many2one('import.info','Import Lot', required=False,
                                    help="Import Information, it is required for manipulation if import info in invoices."),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        #Avoiding use 000 in show name.
        res = [(r['id'], ''.join([a for a in r['name'] if a<>'0'])+'::'+(self.browse(cr,uid,r['id'],context).import_id.name or '')) for r in self.read(cr, uid, ids, ['name',], context)]
        #res = [(r['id'], 'COMO QUIERO') for r in self.read(cr, uid, ids, ['name',], context)]
        return res

stock_production_lot()

