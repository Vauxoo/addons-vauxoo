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

from tools.translate import _

class ifrs_ifrs(osv.osv):

    _name = 'ifrs.ifrs'
    _rec_name = 'code'
    _columns = {
        'name' : fields.char('Name', 128, required = True ),
        'company_id' : fields.many2one('res.company', string='Company', ondelete='cascade' ),
        'title' : fields.char('Title', 128, required = True, translate = True ),
        'code' : fields.char('Code', 128, required = True ),
        'description' : fields.text('Description'),

        'ifrs_lines_ids' : fields.one2many('ifrs.lines', 'ifrs_id', 'IFRS lines' ),

        'state': fields.selection( [
            ('draft','Draft'),
            ('ready', 'Ready'),
            ('done','Done'),
            ('cancel','Cancel') ],
            'State', required=True ),

        'fiscalyear_id' : fields.many2one('account.fiscalyear', 'Fiscal Year' ),
        'do_compute' : fields.boolean('Compute'),
        'ifrs_ids':fields.many2many('ifrs.ifrs', 'ifrs_m2m_rel', 'parent_id', 'child_id', string='Other Reportes',)
    }

    _defaults = {
        'state' : 'draft',
    }

    def compute(self, cr, uid, ids, context=None):
        if context is None: context = {}
        fy = self.browse(cr, uid, ids, context=context)[0]
        context.update({'whole_fy':True, 'fiscalyear':fy.fiscalyear_id.id})
        
        return self.write(cr,uid,ids,{'do_compute':True},context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'do_compute' : False,
        })
        res = super(ifrs_ifrs, self).copy(cr, uid, id, default, context)
        return res

ifrs_ifrs()

class ifrs_lines(osv.osv):

    _name = 'ifrs.lines'
    _parent_store = True
#    _parent_name = "parent_id"
    _order = 'sequence, type'

    def _get_sum_total(self, cr, uid, brw, context = None):
        if context is None: context = {}
        c = context.copy()
        res = 0
        for t in brw.total_ids:
            res += self._get_sum( cr, uid, t.id, context = c )
        if brw.operator <> 'without':
            res2=0
            for o in brw.operand_ids:
                res2 += self._get_sum( cr, uid, o.id, context = c )
            if brw.operator == 'subtract':
                res -= res2
            elif brw.operator == 'percent':
                res =  res2 != 0 and (100 * res / res2) or 0.0
            elif brw.operator == 'ratio':
                res =  res2 != 0 and (res / res2) or 0.0
            elif brw.operator == 'product':
                res =  res * res2
        return res

    def _get_sum( self, cr, uid, id, context = None ):
        fy_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        if context is None: context = {}
        res = 0
        c = context.copy()
        brw = self.browse( cr, uid, id, context = c )
        
        #~ Assembling context
        
        #~ Generic context applicable to the different types
        
        if not c.get('fiscalyear'):
            c['fiscalyear']=fy_obj.find(cr,uid,dt=None,context=c)
        
        if not c.get('period_from',False) and not c.get('period_to',False):
            if context.get('whole_fy',False):
                c['period_from'] = period_obj.search(cr,uid,[('fiscalyear_id','=',c['fiscalyear']),('special','=',True)])
                if not c['period_from']:
                    raise osv.except_osv(_('Error !'), _('There are no special period in %s')%(fy_obj.browse(cr,uid,c['fiscalyear'],context=c).name))
                c['period_from']=c['period_from'][0]
            c['period_to'] =period_obj.search(cr,uid,[('fiscalyear_id','=',c['fiscalyear'])])[-1]
        
        c.get('periods') and c.pop('periods')
        c.get('initial_bal') and c.pop('initial_bal')
        
        if brw.type == 'detail':
            if brw.acc_val=='init':
                period_ids = period_obj.build_ctx_periods_initial(cr, uid, c['period_from'])
                c['periods'] = period_ids
#                period_company_id = period_obj.browse(cr, uid, c['period_from'], context=context).company_id.id
##                c['period_to']= period_obj.previous(cr, uid, c['period_from'],context= c) or c['period_from']
#                period_to = period_obj.previous(cr, uid, c['period_from'],context= c) or c['period_from']
#                c['period_from'] = period_obj.search(cr, uid, [('company_id', '=', period_company_id),('special', '=', True), ('fiscalyear_id','=',context.get('fiscalyear'))], order='date_start', limit=1)[0]
 #               period_from_to = period_obj.browse(cr, uid, [c['period_to'], c['period_from']], context=context)
#                if period_from_to[0].date_start <> period_from_to[1].date_start:
 #                   c['period_to'] = period_to
  #              else:
   #                 c['period_to'] = c['period_from']
##                c['period_from'] = period_obj.previous(cr, uid, c['period_from'],context= c) or c['period_from']
                if not c['period_from']:
                    raise osv.except_osv(_('Error !'), _('prueba001 %s')%(period_obj.browse(cr,uid,c['period_from'],context=c).name))
##                c['period_to']=c['period_from']


            elif brw.acc_val=='var':
                if context.get('whole_fy',False):
                    c['period_from'] =period_obj.search(cr,uid,[('fiscalyear_id','=',c['fiscalyear'],)])
                    if not c['period_from']:
                        raise osv.except_osv(_('Error !'), _('There are no periods in %s')%(fy_obj.browse(cr,uid,c['fiscalyear'],context=c).name))
                    
                if isinstance( c['period_from'], (int, long) ):
                    c['period_from']=c['period_from']
                else:
                    c['period_from']=c['period_from'][1]
                    
        elif brw.type == 'total':
            if brw.comparison <> 'without':
                c2 = c.copy()

                print "c2['period_from']",c2['period_from']
                print "c2['period_to']",c2['period_to']

                c2['period_from'] = period_obj.previous(cr, uid, c2['period_from'],context= c2)
                if not c2['period_from']:
                    raise osv.except_osv(_('Error !'), _('There are previous period to %s')%(period_obj.browse(cr,uid,c['period_from'],context=c).name))
                c2['period_to']=c2['period_from']
                
                print "c2['period_from']",c2['period_from']
                print "c2['period_to']",c2['period_to']
        
        
        #~ Stuffing the sum
        brw = self.browse( cr, uid, id, context = c )
        
        if brw.type == 'abstract':
            pass
        elif brw.type == 'constant':
            if brw.constant_type == 'period_days':
                res = period_obj._get_period_days(cr, uid, c['period_from'], c['period_to'])
            elif brw.constant_type == 'fy_periods':
                res = fy_obj._get_fy_periods(cr, uid, c['fiscalyear'])
            elif brw.constant_type == 'fy_month':
                res = fy_obj._get_fy_month(cr, uid, c['fiscalyear'],c['period_to'])
        elif brw.type == 'detail':
            analytic = [an.id for an in brw.analytic_ids]
            if analytic:
                c['analytic'] = analytic
            c['partner_detail'] = c.get('partner_detail')
            for a in brw.cons_ids:
                if brw.value == 'debit':
                    res += a.debit
                elif brw.value == 'credit':
                    res += a.credit
                else:
                    res += a.balance
                    
        elif brw.type == 'total':
            res = self._get_sum_total(cr, uid, brw, context = c)
            if brw.comparison <> 'without':
                res2=0
                #~ TODO: Write definition for previous periods
                #~ that will be the arguments for the new brw.
                
                brw = self.browse( cr, uid, id, context = c2 )
                res2 = self._get_sum_total(cr, uid, brw, context = c2)

                print 100*'*'
                print 'RES 1 DE COMPARACION ', res
                print 'RES 2 DE COMPARACION ', res2


                if brw.comparison == 'subtract':
                    res -= res2
                elif brw.comparison == 'percent':
                    res =  res2 != 0 and (100 * res / res2) or 0.0
                elif brw.comparison == 'ratio':
                    res =  res2 != 0 and (res / res2) or 0.0
            
                print 'RES DESPUES DE COMPARACION ', res
        return brw.inv_sign and (-1.0 * res) or res 

    def _consolidated_accounts_sum( self, cr, uid, ids, field_name, arg, context = None ):
        if context is None: context = {}
        res = {}
        for id in ids:
            res[id] = self._get_sum( cr, uid, id, context = context )
        return res

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
    def _get_changes_on_ifrs(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = []
        ifrs_brws = self.pool.get('ifrs.ifrs').browse(cr, uid, ids, context = context)
        for brw in ifrs_brws:
            if brw.do_compute:
                for l in brw.ifrs_lines_ids:
                    res.append(l.id)
                #~ TODO: write back False to brw.do_compute with SQL
                #~ INCLUDE A LOGGER
        print 100*"*"
        print 'RECOMPUTING LINES ',res
        return res
        
    _columns = {
        'sequence' : fields.integer( 'Sequence', required = True ),
        'name' : fields.char( 'Name', 128, required = True, translate = True ),
        'type': fields.selection(
           [
                ('abstract','Abstract'),
                ('detail', 'Detail'),
                ('constant', 'Constant'),
                ('total','Total') ] ,
            string = 'Type',
            required = True ),
        'constant_type': fields.selection(
           [
                ('period_days','Days of Period'),
                ('fy_periods',"FY's Periods"),
                ('fy_month',"FY's Month"),
            ],
            string = 'Constant Type',
            required = False ),
        'ifrs_id' : fields.many2one('ifrs.ifrs', 'IFRS', required = True ),
        'amount' : fields.function( _consolidated_accounts_sum, method = True, type='float', string='Amount', 
            store={
                    'ifrs.ifrs':(_get_changes_on_ifrs,['do_compute'],15)
            },
            help="This field will update when you click the compute button in the IFRS doc form"
            ),

        'cons_ids' : fields.many2many('account.account', 'ifrs_account_rel', 'ifrs_lines_id', 'account_id', string='Consolidated Accounts' ),
        'analytic_ids' : fields.many2many('account.analytic.account', 'ifrs_analytic_rel', 'ifrs_lines_id', 'analytic_id', string='Consolidated Analytic Accounts' ),

        
        'parent_id' : fields.many2one('ifrs.lines','Parent', select=True, ondelete ='set null', domain="[('ifrs_id','=',parent.id), ('type','=','total'),('id','!=',id)]"),

        'parent_abstract_id' : fields.many2one('ifrs.lines','Parent Abstract', select=True, ondelete ='set null', domain="[('ifrs_id','=',parent.id),('type','=','abstract'),('id','!=',id)]"),

        'parent_right' : fields.integer('Parent Right', select=1 ),
        'parent_left' : fields.integer('Parent Left', select=1 ),

    'level': fields.function(_get_level, string='Level', method=True, type='integer',
         store={
            'ifrs.lines': (_get_children_and_total, ['parent_id'], 10),
         }),

        'operand_ids' : fields.many2many('ifrs.lines', 'ifrs_operand_rel', 'ifrs_parent_id', 'ifrs_child_id', string='Operands' ),

        'operator': fields.selection( [
            ('subtract', 'Subtraction'),
            ('percent', 'Percentage'),
            ('ratio','Ratio'),
            ('product','Product'),
            ('without','')
            ],
            'Operator', required=False ,
            help='Leaving blank will not take into account Operands'),

        'comparison': fields.selection( [
            ('subtract', 'Subtraction'),
            ('percent', 'Percentage'),
            ('ratio','Ratio'),
            ('without','')],
            'Make Comparison', required=False ,
            help='Make a Comparison against the previous period.\nThat is, period X(n) minus period X(n-1)\nLeaving blank will not make any effects'),
        
        'acc_val': fields.selection( [
            ('init', 'Initial Values'),
            ('var','Variation in Periods'),
            ('fy', ('FY All'))],
            'Accounting Spam', required=False,
            help='Leaving blank means YTD'),

        'value': fields.selection( [
            ('debit', 'Debit'),
            ('credit','Credit'),
            ('balance', 'Balance')],
            'Accounting Value', required=False,
            help='Leaving blank means Balance'),

        'total_ids' : fields.many2many('ifrs.lines','ifrs_lines_rel','parent_id','child_id',string='Total'),
        
        'inv_sign' : fields.boolean('Change Sign to Amount'),
        
        'invisible' : fields.boolean('Invisible'),
    }

    _defaults = {
        'type' : 'abstract',
        'invisible' : False,
        'acc_val' : 'fy',
        'value' : 'balance'
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
