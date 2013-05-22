# -*- encoding: utf-8 -*-
# Author=Nhomar Hernandez nhomar@vauxoo.com
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

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import release


class stock_tracking(osv.Model):
    _inherit = "stock.tracking"
    _columns = {
        'import_id': fields.many2one('import.info', 'Import Lot', required=False,
            help="Import Information, it is required for manipulation if import info in invoices."),
#        'import_product_id': fields.related('import_id','product_id', type='many2one',
#        relation='product.product', readonly=True, string='Product'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        # Avoiding use 000 in show name.
        res = [(r['id'], ''.join([a for a in r['name'] if a != '0'])+'::'+(
            self.browse(cr, uid, r['id'], context).import_id.name or '')) \
            for r in self.read(cr, uid, ids, ['name', ], context)]
        return res


class stock_move_constraint(osv.Model):
    """
    stock_move for validations in the move of inventory
    """
    _inherit = 'stock.move'
    _columns = {}

    def _check_product_qty(self, cr, uid, ids, context=None):
        """Check if quantity of product planified on import info document is 
        bigger than this qty more qty already received with this tracking lot
        """
#        Product qty planified.
# product_qty_p=[{'product_id':p.product_id.id,'qty':p.qty,'uom_id':p.uom_id.id}
# for p in move.tracking_id.import_id.product_info_ids if
# p.product_id.id==move.product_id.id]
        product_import_info_obj = self.pool.get('product.import.info')
        product_uom_obj = self.pool.get('product.uom')
        for move in self.browse(cr, uid, ids, context=context):
            #~ print "move.product_id.id",move.product_id.id
            #~ print "move.product_uom",move.product_uom.id
            #~ print "move.product_qty",move.product_qty
            #~ print "move.product_packaging",move.product_packaging
            import_id = move.tracking_id and move.tracking_id.import_id and\
            move.tracking_id.import_id.id or False
            #~ print 'import_id es',import_id
            if import_id:
                product_import_info_ids = product_import_info_obj.search(
                    cr, uid, [('import_id', '=', import_id),
                    ('product_id', '=', move.product_id.id)], context=context)
                for product_import_info in product_import_info_obj.browse(
                    cr, uid, product_import_info_ids, context=context):
                    #~ print "product_import_info.product_id.id",product_import_info.product_id.id
                    #~ print "product_import_info.uom_id",product_import_info.uom_id.id
                    #~ print "product_import_info.qty",product_import_info.qty
                    qty_dflt_stock = product_uom_obj._compute_qty(cr, uid,
                        move.product_uom.id, move.product_qty,
                        move.product_id.uom_id.id)
                    qty_dflt_import = product_uom_obj._compute_qty(cr, uid,
                        product_import_info.uom_id.id, product_import_info.qty,
                        product_import_info.product_id.uom_id.id)

                    if qty_dflt_stock > qty_dflt_import:
                        #~ print 'cantidad mayor',qty_dflt_stock,'>',qty_dflt_import
                        return False

        return True

    def _check_if_product_in_track(self, cr, uid, ids, move, context=None):
        """
        check if product at least exist in import track
        """
        #      Validar, que si tiene pack_control, valide que tenga el
        #      informacion de importacino y que ademas exista el producto en
        #      este import_info
        #      Si no tiene pack_control, y ademas le agregaste import_info,
        #      obligalo a que quite el import_info ya que no es necesario.
        #      Si no tiene pack_control y no tiene import_info, dejalo pasar
        # print "move.state",move.state
        # print "import_id",import_id
        # print "move.product_id.pack_control",move.product_id.pack_control
        if move.state != 'done':
            # purchase o sale, generate a stock.move with state confirmed or
            # draft, then not validate with these states.
            return True
        import_id = move.tracking_id and move.tracking_id.import_id or False
        if move.product_id.pack_control:
            if not import_id:
                return False
            # return any( [True for p in
            # move.tracking_id.import_id.product_info_ids if move.product_id.id
            # == p.product_id.id] )#optimiza codigo, pero no perfomance
            for p in move.tracking_id.import_id.product_info_ids:
                if move.product_id.id == p.product_id.id:
                    # Optimizando perfomance: En cuanto lo encuentre en la
                    # iteracion, se detenga y lo retorne y ya no siga buscando
                    # mas
                    return True
            return False
        elif import_id:
            return False
        return True

    def onchange_track_id(self, cr, user, track_id, context=None):
        """
        Return a dict that contains new values, and context
        @param cr: cursor to database
        @param user: id of current user
        @param track_id: latest value from user input for field track_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: return a dict that contains new values, and context
        """
        return {
            'value': {},
            'context': {},
        }

    def _check_import_info(self, cr, uid, ids, context=None):
        """ Checks track lot with import information is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, context=context):
            # Check if i need to verify the track for import info.
            ex = True
            if not move.tracking_id and (move.state == 'done' and(
                (move.product_id.pack_control and move.location_id.usage == 'production') or
                (move.product_id.pack_control and move.location_id.usage == 'internal') or
                (move.product_id.pack_control and move.location_id.usage == 'inventory') or
                (move.product_id.pack_control and move.location_dest_id.usage == 'production') or
                (move.product_id.pack_control and move.location_id.usage == 'supplier') or
                (move.product_id.pack_control and move.location_dest_id.usage == 'customer')
               )):
                ex = False

            if not self._check_if_product_in_track(cr, uid, ids, move, context):
                ex = False
            if not self._check_product_qty(cr, uid, [move.id], context):
                ex = False
        return ex

#    def _check_import_info(self, cr, uid, ids, context=None):
#        print "I checked"
#        return True

    _constraints = [(
        _check_import_info, 'You must assign a track lot with import information for this product, if it is assigned verify if you have enought products planified on this import document or at least if the product exist in the list of products in this import document, if you are trying to generate a new pack with the wizard it is not possible if the product is checked as Pack Control, check with your product manager to make the analisys of the situation.\nOther error can be on product_qty field,  Product qty is bigger than product qty on import info.', ['tracking_id'])]


class stock_picking(osv.Model):
    _inherit = "stock.picking"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        # print "************AQUI ENTRO"
        # Copy & paste original function -> Add new functionallity.
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        address_obj = self.pool.get('res.partner.address')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            payment_term_id = False
            partner = picking.address_id and picking.address_id.partner_id
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)
            if release.version >= 6.1:
                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = partner.property_account_receivable.id
                    payment_term_id = picking.sale_id.payment_term.id
                else:
                    account_id = partner.property_account_payable.id

                address_contact_id, address_invoice_id = \
                    self.pool.get('res.partner').address_get(cr, uid, [
                        partner.id], ['contact', 'invoice']).values()
                address = address_obj.browse(
                    cr, uid, address_contact_id, context=context)
            else:
                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = partner.property_account_receivable.id
                    payment_term_id = self._get_payment_term(cr, uid, picking)
                else:
                    account_id = partner.property_account_payable.id

                address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cr, uid, picking).values()
                address = address_obj.browse(
                    cr, uid, address_contact_id, context=context)

            comment = self._get_comment_invoice(cr, uid, picking)
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or '') + ', ' + (picking.name or ''),
                    'origin': (invoice.origin or '') + ', ' + (picking.name \
                        or '') + (picking.origin and (':' + picking.origin) or ''),
                    'comment': (comment and (invoice.comment and invoice.\
                        comment+"\n"+comment or comment)) or (invoice.comment \
                        and invoice.comment or ''),
                    'date_invoice': context.get('date_inv', False),
                    'user_id': uid
                }
                invoice_obj.write(cr, uid, [
                                  invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': picking.name,
                    'origin': (picking.name or '') + (picking.origin and (
                        ':' + picking.origin) or ''),
                    'type': inv_type,
                    'account_id': account_id,
                    'partner_id': address.partner_id.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'comment': comment,
                    'payment_term': payment_term_id,
                    'fiscal_position': partner.property_account_position.id,
                    'date_invoice': context.get('date_inv', False),
                    'company_id': picking.company_id.id,
                    'user_id': uid
                }
                cur_id = self.get_currency_id(cr, uid, picking)
                if cur_id:
                    invoice_vals['currency_id'] = cur_id
                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cr, uid, invoice_vals,
                                                context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                origin = move_line.picking_id.name or ''
                if move_line.picking_id.origin:
                    origin += ':' + move_line.picking_id.origin
                if group:
                    name = (picking.name or '') + '-' + move_line.name
                else:
                    name = move_line.name

                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = move_line.product_id.product_tmpl_id.\
                        property_account_income.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                            property_account_income_categ.id
                else:
                    account_id = move_line.product_id.product_tmpl_id.\
                        property_account_expense.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                            property_account_expense_categ.id

                price_unit = self._get_price_unit_invoice(cr, uid,
                                                          move_line, inv_type)
                discount = self._get_discount_invoice(cr, uid, move_line)
                tax_ids = self._get_taxes_invoice(cr, uid, move_line, inv_type)
                account_analytic_id = self._get_account_analytic_invoice(
                    cr, uid, picking, move_line)

                # set UoS if it's a sale and the picking doesn't have one
                uos_id = move_line.product_uos and move_line.product_uos.id or False
                if not uos_id and inv_type in ('out_invoice', 'out_refund'):
                    uos_id = move_line.product_uom.id
                account_id = self.pool.get('account.fiscal.position').map_account(
                    cr, uid, partner.property_account_position, account_id)
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': move_line.product_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': move_line.product_uos_qty or move_line.product_qty,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_analytic_id': account_analytic_id,
                    # Start Custom Code
                    'move_id': move_line.id,
                    'tracking_id': move_line.tracking_id and move_line.\
                        tracking_id.id,
                    # End Custom Code
                }, context=context)
                self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
            }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
        }, context=context)
        return res

"""
class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids,
            journal_id, group, type, context=context)
        for picking_id in res.keys():
            invoice_id = res[picking_id]
            picking = self.browse(cr, uid, [picking_id], context=context)[0]
            "SELECT id, product_id FROM account_invoice_line"

            #invoice_obj.write(cr, uid, [invoice_id] {
                #'picking_id': picking_id,
                #'tracking_id': picking.tracking_id,
            #})
        #res[picking.id] = invoice_id
        return res
"""
