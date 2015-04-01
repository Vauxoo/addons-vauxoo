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
from openerp import models, api


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        if line.get('sm_id', False):
            res['sm_id'] = line['sm_id']
        return res


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _anglo_saxon_purchase_stock_move_lines(self, cr, uid, res,
                                               context=None):
        ail_obj = self.pool.get('account.invoice.line')
        fp_obj = self.pool.get('account.fiscal.position')
        rex = []
        for line in res:
            if line.get('invl_id', False):
                ail_brw = ail_obj.browse(cr, uid, line.get('invl_id'), context=context)
                pp_brw = ail_brw.product_id
                if pp_brw and pp_brw.valuation == 'real_time' and \
                        pp_brw.type != 'service':
                    a = None
                    oa = pp_brw.property_stock_account_input and \
                        pp_brw.property_stock_account_input.id or \
                        pp_brw.categ_id.property_stock_account_input_categ and\
                        pp_brw.categ_id.property_stock_account_input_categ.id
                    if oa:
                        fpos = ail_brw.invoice_id.fiscal_position or False
                        a = fp_obj.map_account(cr, uid, fpos, oa)
                    if a == line['account_id'] and ail_brw.move_id:
                        line['sm_id'] = ail_brw.move_id.id
            rex.append(line)
        return rex

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line,
                    self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(
            cr, uid, invoice_id, context=context)
        if inv.type in ('out_invoice', 'out_refund'):
            res = self._anglo_saxon_sale_stock_move_lines(
                cr, uid, res, context=context)
        elif inv.type in ('in_invoice', 'in_refund'):
            res = self._anglo_saxon_purchase_stock_move_lines(
                cr, uid, res, context=context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
