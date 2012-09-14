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
            if len(moves)==0:
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
            
    _columns = {
        'consumed' : fields.function(_check_boolean, string='consumed?', type='boolean', help="indicates if product to consume have been consumed or canceled"),
        'len_move' : fields.function(_check_len_move, string='moves', type='float')
    }
    
    def action_finished_consume(self,cr,uid,ids,context={}):
        stock_move = self.pool.get('stock.move')
        for production in self.browse(cr,uid,ids,context=context):
            for moves in production.move_lines:
                stock_move.write(cr,uid,[moves.id],{'state':'cancel'})
        return True
    
    def action_finish(self,cr,uid,ids,context={}):
        stock_move = self.pool.get('stock.move')
        for production in self.browse(cr,uid,ids,context=context):
            for moves in production.move_created_ids:
                stock_move.write(cr,uid,[moves.id],{'state':'cancel'})
        try:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce_done', cr)
        except:
            pass
        return True

mrp_production()

