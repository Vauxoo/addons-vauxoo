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
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
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
        if context is None:
            context = {}
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
        if context is None:
            context = {}
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
        if context is None:
            context = {}
        return {
            'value': {},
            'context': {},
        }

    def _check_import_info(self, cr, uid, ids, context=None):
        """ Checks track lot with import information is assigned to stock move or not.
        @return: True or False
        """
        if context is None:
            context = {}
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
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        if context is None:
            context = {}
        invoice_line_data = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=context)
        invoice_line_data.update({
            'move_id': move_line.id,
            'tracking_id': move_line.tracking_id and move_line.\
                tracking_id.id,
        })
        return invoice_line_data

