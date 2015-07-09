#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
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

PURCHASE_ORDER_TYPE = [
    ('materials', 'Materials'),
    ('service', 'Services'),
]


class stock_picking(osv.Model):
    _inherit = 'stock.picking'
    _columns = {
        'responsible_id': fields.many2one('res.users', 'Responsible'),
    }


class stock_picking_in(osv.Model):
    _inherit = 'stock.picking.in'
    _columns = {
        'responsible_id': fields.many2one('res.users', 'Responsible'),
    }


class stock_picking_out(osv.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'responsible_id': fields.many2one('res.users', 'Responsible'),
    }
