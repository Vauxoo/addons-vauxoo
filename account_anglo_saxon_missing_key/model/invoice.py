# coding: utf-8
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

from openerp.osv import osv


class AccountInvoiceLine(osv.osv):
    _inherit = "account.invoice.line"

    def _anglo_saxon_sale_move_lines(self, cr, uid, i_line, res, context=None):
        res = super(AccountInvoiceLine, self)._anglo_saxon_sale_move_lines(
            cr, uid, i_line, res, context=context)
        if res:
            res[0]['invl_id'] = res[1]['invl_id'] = i_line.id

        return res

    def _anglo_saxon_purchase_move_lines(self, cr, uid, i_line, res, context=None):
        res = super(AccountInvoiceLine,
                    self)._anglo_saxon_purchase_move_lines(
                        cr, uid, i_line, res, context=context)
        if res:
            res[0]['invl_id'] = i_line.id

        return res
