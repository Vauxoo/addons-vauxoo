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

from osv import fields, osv

from tools.translate import _

class stock_invoice_onshipping_psm(osv.osv_memory):

    _inherit = "stock.invoice.onshipping"

    _columns = {
        'group_by_product': fields.boolean("Group by product"),
    }

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(stock_invoice_onshipping_psm,self).create_invoice(cr, uid, ids, context=context)
        
        print 'esto es res',res
        
        return res
        
        
        
stock_invoice_onshipping_psm()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
