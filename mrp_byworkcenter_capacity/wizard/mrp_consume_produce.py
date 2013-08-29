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
from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.tools.translate import _


class mrp_consume(osv.TransientModel):
    _inherit = 'mrp.consume'
    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string=_('Manufacturing Order'),
            help=_('Manufacturing Order')),
        'wo_lot_id': fields.many2one(
            'mrp.workoder.lot',
            required=True,
            string=_('Scheduled Work Orders Lots'),
            help=_('Scheduled Work Orders Lots.')),
    }

    _defaults = {
        'production_id': lambda s, c, u, ctx: ctx.get('active_id', False), 
    }
