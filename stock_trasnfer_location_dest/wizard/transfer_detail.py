# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, fields, api, _


class stock_transfer_details(models.TransientModel):

    _inherit = 'stock.transfer_details'

    def default_get(self, cr, uid, l_fields, context=None):
        context = context or {}
        res = super(stock_transfer_details, self).default_get(cr, uid,
                                                              l_fields,
                                                              context=context)
        print res
        return res

    dest_location_id = fields.Many2one('stock.lcation',
                                       string='Destination Location',
                                       help='Destination Location of the '
                                       'transfer if you change this '
                                       'location, the new location '
                                       'will be established in all lines '
                                       'that will be transferred')
    change_location = fields.Boolean('Change Location',
                                     help='Check if you want to change the '
                                     'destination location of this transfer')

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
