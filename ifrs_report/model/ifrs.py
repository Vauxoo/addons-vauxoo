#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Katherine Zaoral <katherine.zaoral@vauxoo.com>
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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

from osv import osv
from osv import fields

class ifrs_ifrs(osv.osv):

    _name = 'ifrs.ifrs'
    _columns = {
        'name' : fields.char('Name', 128, required = True ),
        'company_id' : fields.many2one('res.company', string='Company', ondelete='cascade', required = True ),
        'title' : fields.text('Title', required = True ),
        'ifrs_lines_ids' : fields.one2many('ifrs.lines', 'ifrs_id', 'IFRS lines' ),

        'state': fields.selection( [
            ('draft','Draft'),
            ('ready', 'Ready'),
            ('done','Done'),
            ('cancel','Cancel') ],
            'State', required=True ),

        'fiscalyear_id' : fields.many2one('account.fiscalyear', 'Fiscal Year', required = True ),
    }

    _defaults = {
        'state' : 'draft',
    }

ifrs_ifrs()

class ifrs_lines(osv.osv):

    _name = 'ifrs.lines'
    _parent_store = True
#    _parent_name = "parent_id"
    _order = 'sequence, type'

    def _get_sum( self, cr, uid, id, context = None ):
        if context is None: context = {}
        res = 0
        brw = self.browse( cr, uid, id, context = context )

        if brw.type == 'abtract':
            pass
        elif brw.type == 'detail':
            for a in brw.cons_ids:
                res += a.balance
        elif brw.type == 'total':
            for c in brw.total_ids:
                res += self._get_sum( cr, uid, c.id, context = context )
            if brw.operator:
                res2=0
                for o in brw.operand_ids:
                    res2 += self._get_sum( cr, uid, o.id, context = context )
                res = brw.operator == 'subtract' and (res - res2) or (res2 != 0 and (res / res2) or 0.0)  
        
        return brw.inv_sign and (-1.0 * res) or res 

    def _consolidated_accounts_sum( self, cr, uid, ids, field_name, arg, context = None ):
        if context is None: context = {}
        res = {}
        for id in ids:
            res[id] = self._get_sum( cr, uid, id, context = context )
        return res
    
#    def _determine_parent_id(self, cr, uid, ids, field_name, arg, context = None):
#        if context is None: context = {}
#        res = {}.fromkeys(ids,False)
#        print "Entre a _determine_parent_id"
#        print "ids = '%s' - field_name = '%s' " % (ids, field_name) # field_name es el nombre del campo parent_id
#        
#        cr.execute('select parent_id,child_id from ifrs_lines_rel where child_id in (%s)' %', '.join([str(id) for id in ids]))
#                
#        for t in cr.dictfetchall():
#            res[ int(t['child_id']) ] =  int(t['parent_id']) 
#            print "child : %s , parent : %s" % (t['child_id'], t['parent_id'])
#        print res
#        return res

#    def _determine_list_totalids(self, cr, uid, ids, context=None):
#        res = {}
#        if context is None: context = {}
#        print "Entre a _determine_list_parent"
#        print "ids = '%s'" % (ids) # El id del ifrs.line actual
#        
#        for ifrs_l_id in ids: #Obtengo el id del ifrs.line actual
#            ifrs_l = self.browse( cr, uid, ifrs_l_id, context = context )
#            for total_id in ifrs_l.total_ids: # Recorro los total ids
#                res[total_id.id] = True # Guardo el id del ifrs.line actual en el id de uno de los ifrs.line que posee, es decir guardo el parent_id en uno de los total_ids
#                print total_id.id
#        return res.keys() # Devuelvo las keys, y las recibe el metodo principal del parent_id, el _determine_parent_id en la variable ids
    

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for ifrs_line in self.browse(cr, uid, ids, context=context):
            level = 0
            parent = ifrs_line.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[ifrs_line.id] = level
        return res

    def _get_children_and_total(self, cr, uid, ids, context=None):
        #this function search for all the children and all consolidated children (recursively) of the given total ids
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.total_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_total(cr, uid, ids3, context)
        return ids2 + ids3

    _columns = {
        'sequence' : fields.integer( 'Sequence', required = True ),
        'name' : fields.char( 'Name', 128, required = True ),
        'type': fields.selection(
           [
                ('abstract','Abstract'),
                ('detail', 'Detail'),
                ('total','Total') ] ,
            string = 'Type',
            required = True ),
		'ifrs_id' : fields.many2one('ifrs.ifrs', 'IFRS', required = True ),
        'amount' : fields.function( _consolidated_accounts_sum, method = True, type='float', string='Amount', store=True),
        

		'cons_ids' : fields.many2many('account.account', 'ifrs_account_rel', 'ifrs_lines_id', 'account_id', string='Consolidated Accounts' ),

        
     	'parent_id' : fields.many2one('ifrs.lines','Parent', select=True, ondelete ='set null', domain="[('ifrs_id','=',parent.id), ('type','=','total'),('id','!=',id)]"),

		'parent_abstract_id' : fields.many2one('ifrs.lines','Parent Abstract', select=True, ondelete ='set null', domain="[('ifrs_id','=',parent.id),('type','=','abstract'),('id','!=',id)]"),

#,('id','!=',id)

	#~ 'total_ids': fields.one2many('ifrs.lines', 'parent_id', string='Child'),



        'parent_right' : fields.integer('Parent Right', select=1 ),
        'parent_left' : fields.integer('Parent Left', select=1 ),

	'level': fields.function(_get_level, string='Level', method=True, type='integer',
         store={
            'ifrs.lines': (_get_children_and_total, ['parent_id'], 10),
         }),

        'operand_ids' : fields.many2many('ifrs.lines', 'ifrs_operand_rel', 'ifrs_parent_id', 'ifrs_child_id', string='Operands' ),

        'operator': fields.selection( [
            ('subtract', 'Subtraction'),
            ('ratio','Ratio')],
            'Operator', required=False ),

        'total_ids' : fields.many2many('ifrs.lines','ifrs_lines_rel','parent_id','child_id',string='Total'),
        'inv_sign' : fields.boolean('Change Sign to Amount')
   	#'parent_id': fields.function(_determine_parent_id, method=True, relation='ifrs.lines', type='many2one', string='Parent', store={'ifrs.lines':(_determine_list_totalids, ['total_ids'], 15),}),


    }

    _defaults = {
        'type' : 'abstract',
		#'sequence': lambda obj, cr, uid, context: uid,
    }


    def _check_description(self, cr, user, ids):
        for s in self.browse(cr,user,ids):
			#if s.type=='total' and s.parent_id.type!='abstract':
            #    return False
			pass
        return True
    
    _constraints = [
        (_check_description, ('Error: Los padres de las lineas ifrs de tipo total solo pueden tener padres de tipo abstract'), ['parent_id']),
    ]

    _sql_constraints = [('sequence_ifrs_id_unique','unique(sequence,ifrs_id)', 'The sequence already have been set in another IFRS line')]


ifrs_lines()


#~ pregunta. comprobacion de la linea... lo hace cuando le da a guardar--- no lo hace a la hora de ingresarlo, puede taer confuciones a la hora que el usuario agregue a mucha gente y luego no sepa a cual se refiere.

#~ buscar, como hacer para que ordene por secuencia, lo que ingreso!
