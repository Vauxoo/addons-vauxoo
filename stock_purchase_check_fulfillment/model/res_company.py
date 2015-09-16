# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
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


class Company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'check_purchase_fulfillment': fields.boolean(
            'Check Purchase Order Fulfillment',
            help=("Tick this option if you want to check for Purchase Order "
                  "Fulfillment")),
    }


class ResPartner(osv.Model):

    _inherit = 'res.partner'
    _columns = {
        'skip_purchase_fulfillment': fields.boolean(
            'Allow Skip Purchase Order Fulfillment',
            help=("Tick this option if you want allow this user to received in"
                  " Excess Quantities ordered in Purchase Order")),
    }
