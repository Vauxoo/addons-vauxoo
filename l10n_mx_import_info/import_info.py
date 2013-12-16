# -*- encoding: utf-8 -*-
# Author=Nhomar Hernandez nhomar@vauxoo.com
# Audited by=
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from openerp.tools.translate import _
from openerp.osv import fields, osv


class import_info(osv.Model):
    _name = "import.info"
    _description = "Information about customs"
    _order = 'name asc'

    def _get_audit(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        prod_obj = self.pool.get('product.product')
        for i in ids:
            chain = ''
            for p in self.browse(cr, uid, [i], context)[0].product_info_ids:
                if not self.browse(cr, uid, [i], context)[0].supplier_id.id in [
                    s.name.id for s in p.product_id.seller_ids]:
                    chain2 = '\nVerify the product: %s the Supplier on this document is not related to this product.\n' % p.product_id.name
                    chain = chain+chain2
            result[i] = chain
        return result

    _columns = {
        'name': fields.char('Number of Operation', 15,
                            help="Transaction Number of tramit Information"),
        'customs': fields.char('Customs', 64,
            help="What Customs was used in your country for import this lot (Generally it is a legal information)"),
        'date': fields.date('Date',
            help="Date of Custom and Import Information (In Document)"),
        'lot_ids': fields.one2many('stock.tracking', 'import_id', 'Production Lot'),
        'rate': fields.float('Exchange Rate', required=True, digits=(16, 4),
            help='Exchange rate informed on Custom House when the transaction was approved'),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            select=1, help="Company related to this document."),
        'supplier_id': fields.many2one('res.partner', 'Supplier', select=1,
            help="Partner who i bught this product related to to this document."),
        'invoice_ids': fields.many2many('account.invoice', 'account_invoice_rel',
            'import_id', 'invoice_id', 'Invoices Related'),
        'product_info_ids': fields.one2many('product.import.info', 'import_id',
            'Products Info', required=False),
        'audit_note': fields.function(_get_audit, method=True, type='text',
            string='Audit Notes'),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').\
            _company_default_get(cr, uid, 'import.info', context=c)
    }
