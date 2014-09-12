# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
# Credits######################################################
#    Coded by: Miguel Delgado <miguel@openerp.com.ve>                      #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Corporacion AMD                                           #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp


class product_product(osv.Model):
    _inherit = "product.product"

    _columns = {
        'track_serial_incoming': fields.boolean('Track Incoming Serial Lots',
                                                help="""Forces to specify a
                                                        Production serial
                                                        incoming Lot for all
                                                        moves containing this
                                                        product"""),
        'track_serial_outgoing': fields.boolean('Track Outgoing Serial Lots',
                                                help="""Forces to specify a
                                                        Production serial
                                                        outgoing Lot for all
                                                        moves containing this
                                                        product"""),
    }
