##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)
#    2004-2010 Tiny SPRL (<http://tiny.be>).
#    2009-2010 Veritos (http://veritos.nl).
#    All Rights Reserved
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

from openerp.osv import osv, fields


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
        'move_id': fields.many2one('stock.move', string="Move line", help="If the invoice was generated from a stock.picking, reference to the related move line."),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
