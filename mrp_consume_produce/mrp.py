# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
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
from osv import osv,fields
from tools.translate import _
import netsvc

class mrp_production(osv.osv):
    _inherit='mrp.production'
    
    def _check_boolean(self,cr,uid,ids,field_name,args,context={}):
        res = {}
        for production in self.browse(cr,uid,ids,context=context):
            moves = [move for move in production.move_lines]
            if len(moves)==0 and production.state<>'draft':
                res[production.id]=True
            else:
                res[production.id]=False
        return res
        
    def _check_len_move(self,cr,uid,ids,field_name,args,context={}):
        res = {}
        for production in self.browse(cr,uid,ids,context=context):
            moves = [move for move in production.move_lines2 if move.state=='done']
            res[production.id]=len(moves)
        return res
        
    def _check_len_move_prod(self,cr,uid,ids,field_name,args,context={}):
        res = {}
        for production in self.browse(cr,uid,ids,context=context):
            res[production.id] = False
            if len(production.move_created_ids2) > 0:
                res[production.id] = True
        return res
            
    _columns = {
        'consumed' : fields.function(_check_boolean, method=True, string='consumed?', type='boolean', help="indicates if product to consume have been consumed or canceled"),
        'len_move' : fields.function(_check_len_move, method=True, string='moves', type='float'),
        'len_move_prod' : fields.function(_check_len_move_prod, method=True, string='produced', type='boolean',),
    }
    
    def action_finished_consume(self,cr,uid,ids,context={}):
        stock_move = self.pool.get('stock.move')
        for production in self.browse(cr,uid,ids,context=context):
            for moves in production.move_lines:
                stock_move.write(cr,uid,[moves.id],{'state':'cancel'})
        return True
    
    def action_finish(self,cr,uid,ids,context={}):
        stock_move = self.pool.get('stock.move')
        stock_picking= self.pool.get('stock.picking')
        for production in self.browse(cr,uid,ids,context=context):
            for moves in production.move_created_ids:
                stock_move.write(cr,uid,[moves.id],{'state':'cancel'})
        #esta linea marca error por que la relacion de pickings con produccion esta en el modulo mrp_request_return
        #pickings=stock_picking.search(cr, uid, [('production_id','=',production.id),('state','not in',('done','cancel'))], limit=80, context=context)
        moves=stock_move.search(cr, uid, [('production_id','=',production.id),('state','not in',('done','cancel'))], limit=80, context=context)

        if moves:
            raise osv.except_osv(_('Error !'), _('You can not Finish Production With Pickings or Moves in state Open or Reserved!'))
        try:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce_done', cr)
        except:
            pass
        return True

mrp_production()

