# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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


class stock_picking(osv.Model):
    _inherit = 'stock.inventory'

    def unlink(self, cr, uid, ids, context=None):
        stock_inventory = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in stock_inventory:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _(
                    'Stocks can be removed only in draft.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
