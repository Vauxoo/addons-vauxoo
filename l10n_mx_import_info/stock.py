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
from osv import osv
from osv import fields
from tools.translate import _


class stock_tracking(osv.osv):
    _inherit = "stock.tracking"
    _columns={
        'import_id':fields.many2one('import.info','Import Lot', required=False,
                                    help="Import Information, it is required for manipulation if import info in invoices."),
#        'import_product_id': fields.related('import_id','product_id', type='many2one',
#        relation='product.product', readonly=True, string='Product'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        #Avoiding use 000 in show name.
        res = [(r['id'], ''.join([a for a in r['name'] if a<>'0'])+'::'+(self.browse(cr,uid,r['id'],context).import_id.name or '')) for r in self.read(cr, uid, ids, ['name',], context)]
        return res

stock_tracking()


class stock_move_constraint(osv.osv):
    """
    stock_move for validations in the move of inventory
    """
    _inherit = 'stock.move'
    _columns = {}


    def _check_product_qty(self, cr, uid, ids, move, context=None):
        """Check if quantity of product planified on import info document is bigger than
        this qty more qty already received with this tracking lot
        """
#        Product qty planified.
#        product_qty_p=[{'product_id':p.product_id.id,'qty':p.qty,'uom_id':p.uom_id.id} for p in move.tracking_id.import_id.product_info_ids if p.product_id.id==move.product_id.id]
        return True


    def _check_if_product_in_track(self, cr, uid, ids, move, context=None):
        """
        check if product at least exist in import track
        """
        if move.tracking_id.import_id:
            if move.product_id.id in [p.product_id.id for p in move.tracking_id.import_id.product_info_ids]:
                return True
        return False


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
            'value':{ },
            'context':{ },
        }


    def _check_import_info(self, cr, uid, ids, context=None):
        """ Checks track lot with import information is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, context=context):
            #Check if i need to verify the track for import info.
            ex = True
            if not move.tracking_id and \
               (move.state == 'done' and \
               ( \
                   (move.product_id.pack_control and move.location_id.usage == 'production') or \
                   (move.product_id.pack_control and move.location_id.usage == 'internal') or \
                   (move.product_id.pack_control and move.location_id.usage == 'inventory') or \
                   (move.product_id.pack_control and move.location_dest_id.usage == 'production') or \
                   (move.product_id.pack_control and move.location_id.usage == 'supplier') or \
                   (move.product_id.pack_control and move.location_dest_id.usage == 'customer') \
               )): ex = False
            if not self._check_if_product_in_track(cr, uid, ids, move, context): 
                ex = False
                if not self._check_product_qty(cr, uid, ids, move, context): 
                    ex = False
        return ex

#    def _check_import_info(self, cr, uid, ids, context=None):
#        print "I checked"
#        return True

    _constraints = [(_check_import_info,'You must assign a track lot with import information for this product, if it is assigned verify if you have enought products planified on this import document or at least if the product exist in the list of products in this import document, if you are trying to generate a new pack with the wizard it is not possible if the product is checked as Pack Control, check with your product manager to make the analisys of the situation',['tracking_id'])],


stock_move_constraint()

