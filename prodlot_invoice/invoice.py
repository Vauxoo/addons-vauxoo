#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv, orm
from tools.translate import _

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, address_invoice_id=address_invoice_id, currency_id=currency_id, context=context, company_id=company_id)
        res['value'].update({'prodlot_id':False})
        return res
        
    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
}

account_invoice_line()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def action_date_assign(self, cr, uid, ids, *args):
        invoice_line_obj = self.pool.get('account.invoice.line')
        res = False
        for id_ in ids:
            data = self.browse(cr, uid, id_)
            for line in data.invoice_line:
                check_prodlot = False
                if line.product_id.track_outgoing == True:
                    check_prodlot = True
                if check_prodlot is True and not line.prodlot_id:
                    raise osv.except_osv(_('Inpur Error !'), 
                                        _('Add a lot of production to the product: \n' + line.product_id.name))
                else:
                    res = super(account_invoice, self).action_date_assign(cr, uid, ids, args)
        return res
    
