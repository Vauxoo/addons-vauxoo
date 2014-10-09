#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.addons.product import product as Product


class stock_tracking(osv.Model):

    """ this class adds three fields for can have packing control on delivery orders lines
    """
    _inherit = 'stock.tracking'
    _description = _('Need to set the model name')
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'state': fields.selection((('new', 'New'), ('packing', 'Packing'),
                                   ('confirm', 'Confirmed')), 'Status', readonly=True, select=True),
        'ean': fields.char('EAN', size=14, help="The EAN code of the package unit."),
    }

    _defaults = {
        'state': 'new',
    }

    def move_packing(self, cr, uid, ids, context=None):
        """ Allows to pass to packing state
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        self.write(cr, uid, ids, {'state': 'packing'})
        return True

    def pass_confirm(self, cr, uid, ids, context=None):
        """ Allows to pass to confim state
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True

    def _check_ean_key(self, cr, uid, ids, context=None):
        """ Validate ean code
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for pack in self.browse(cr, uid, ids, context=context):
            res = Product.check_ean(pack.ean)
        return res

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean'])]
