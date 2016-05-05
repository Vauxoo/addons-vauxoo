# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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

from openerp import _, api, fields, models


class StockTransferDetails(models.TransientModel):

    _inherit = 'stock.transfer_details'

    @api.multi
    def do_detailed_transfer(self):
        """When the transfer was made, a message in log is displayed
        """
        for transfer_detail in self:
            message = _("<b>Picking transfered</b>\n"
                        "<ul><li><b>Date:</b> %s</li>\n"
                        "</ul>\n") % \
                (fields.datetime.now().
                 strftime("%x %X"))
            transfer_detail.picking_id.message_post(body=message)
        return super(StockTransferDetails, self).do_detailed_transfer()
