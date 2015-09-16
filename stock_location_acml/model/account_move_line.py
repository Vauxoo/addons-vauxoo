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
from openerp.osv import fields, osv


class AccountMoveLine(osv.Model):
    _inherit = "account.move.line"

    """
    """

    _columns = {
        'location_id': fields.related(
            'sm_id', 'location_id', string='Source Location',
            type='many2one', relation='stock.location', store=True,
            help='Location Move Source'),
        'location_dest_id': fields.related(
            'sm_id', 'location_dest_id', type='many2one',
            string='Destination Location', relation='stock.location',
            store=True, help="Location Move Destination")
    }
