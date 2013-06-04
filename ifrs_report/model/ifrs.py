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

_iter_record = 0
_fy = False
_total_record = 0
_period_info_list = []    #~ [ 0 : period_enumerate, 1 : period_id, 2 : period_name ]
_title_line = ' '
_from_currency_id = 0
_to_currency_id = 0

class ifrs_ifrs(osv.osv):

    _name = 'ifrs.ifrs'
    _rec_name = 'code'

    def onchange_company_id(self,cr,uid,ids,company_id,context=None):
        context = context or {}
        context['company_id']=company_id
        res = {'value':{}}
        
        if not company_id: return res
            
        cur_id = self.pool.get('res.company').browse(
                cr, uid, company_id, context=context).currency_id.id
        fy_id = self.pool.get('account.fiscalyear').find(
                cr, uid, context=context)

        res['value'].update({'fiscalyear_id':fy_id})
        res['value'].update({'currency_id':cur_id})
        return res

    _columns = {
        'name' : fields.char('Name', 128, required = True ),
        'company_id' : fields.many2one('res.company', string='Company', ondelete='cascade' ),
        'currency_id': fields.many2one('res.currency', 'Currency', help="Currency at which this report will be expressed. If not selected will be used the one set in the company"),
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
        'company_id': lambda s,c,u,cx: s.pool.get('res.users').browse(
            c,u,u,context=cx).company_id.id,
        'fiscalyear_id': lambda s,c,u,cx: s.pool.get('account.fiscalyear').find(c, u),
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
                period_company_id = period_obj.browse(cr, uid, c['period_from'], context=context).company_id.id
            if not c['period_from']:
                    raise osv.except_osv(_('Error !'), _('prueba001 %s')%(period_obj.browse(cr,uid,c['period_from'],context=c).name))

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


                c2['period_from'] = period_obj.previous(cr, uid, c2['period_from'],context= c2)
                if not c2['period_from']:
                    raise osv.except_osv(_('Error !'), _('There are previous period to %s')%(period_obj.browse(cr,uid,c['period_from'],context=c).name))
                c2['period_to']=c2['period_from']
                
        
        
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

                if brw.comparison == 'subtract':
                    res -= res2
                elif brw.comparison == 'percent':
                    res =  res2 != 0 and (100 * res / res2) or 0.0
                elif brw.comparison == 'ratio':
                    res =  res2 != 0 and (res / res2) or 0.0
            
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
        return res

    def _get_period_print_info(self, cr, uid, ids, period_id, report_type, context=None):
        if context is None: context = {}
        ''' Return all the printable information about period'''

        if report_type == 'all':
            res = 'All Periods of the fiscalyear.'
        else:
            period = self.pool.get('account.period').browse(cr, uid, period_id, context = context)
            res = str(period.name) + ' [' + str(period.code) + ']'

        return res

    def _get_column_name(self, cr, uid, ids, column_num, context=None):
        if context is None: context = {}
        """devuelve string con el nombre del periodo que debe titular ese numero de columna"""

        return self._period_info_list[column_num][2]


    def _get_periods_name_list(self, cr, uid, ids, ifrs_obj, fiscalyear_id, context=None):
        if context is None: context = {}

        """devuelve una lista con la info de los periodos fiscales (numero mes, id periodo, nombre periodo)"""

        period_list = _period_info_list = []
        period_list.append( ('0', None , _title_line ) ) 

        fiscalyear_bwr = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
        
        periods_ids = fiscalyear_bwr._get_fy_period_ids()

        periods = self.pool.get('account.period')
        
        for ii, period_id in enumerate(periods_ids, start=1):
            period_list.append((str(ii), period_id, periods.browse(cr, uid, period_id, context=context).name ))

        _period_info_list = period_list
        _fy = fiscalyear_id
        return _period_info_list

    def exchange(self, cr, uid, ids, from_amount, to_currency_id, from_currency_id, context=None):
        if from_currency_id == to_currency_id:
            return from_amount
        curr_obj = self.pool.get('res.currency')
        return curr_obj.compute(cr, uid, from_currency_id, to_currency_id, from_amount)
    
    def _get_amount_value(self, cr, uid, ids, ifrs_line, period_info, fiscalyear, period_num=None, target_move=None, pd=None, undefined=None, two=None, context=None):
        if context is None: context = {}
        
        '''devuelve la cantidad correspondiente al periodo'''
        from_currency_id = ifrs_line.ifrs_id.company_id.currency_id.id
        to_currency_id = ifrs_line.ifrs_id.currency_id.id

        #print "ifrs_line %s " % ifrs_line
        #print "period_info_list %s _fy %s" % (period_info, fiscalyear)
        print "period_num %s" % period_num
        if period_num:
            if two:
                context = {'period_from': period_num, 'period_to':period_num, 'state': target_move, 'partner_detail':pd, 'fiscalyear':fiscalyear}
            else:
                period_id = period_info[period_num][1]
                context = {'period_from': period_id, 'period_to':period_id, 'state': target_move, 'partner_detail':pd, 'fiscalyear':fiscalyear}
        else:
            context = {'whole_fy': 'True'} 
       
        res = self._get_sum(cr, uid, ifrs_line.id, context = context)
        print "1. res %s" % res
        #if ifrs_line.type == 'detail':
        #    res = self.exchange(res, to_currency_id, from_currency_id)
        #    print "2. res %s" % res
        #elif ifrs_line.type == 'total':
        #    if ifrs_line.operator not in ('percent','ratio'):
        #        if ifrs_line.comparison not in ('percent','ratio','product'):
        #            res = self.exchange(res, to_currency_id, from_currency_id)
        print "3. res %s" % res
        return res

    def _get_partner_detail(self, cr, uid, ids, ifrs_l, context=None):
        ifrs = self.pool.get('ifrs.lines')
        aml_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        res = []
        if ifrs_l.type =='detail':
            ids2 = [lin.id for lin in ifrs_l.cons_ids]
            ids3 = ids2 and account_obj._get_children_and_consol(cr, uid, ids2, context=context) or []
            if ids3:
                cr.execute(""" SELECT rp.id
                    FROM account_move_line l JOIN res_partner rp ON rp.id = l.partner_id
                    WHERE l.account_id IN %s
                    GROUP BY rp.id 
                    ORDER BY rp.name ASC""", ( tuple(ids3), ) 
                    )
                dat = cr.dictfetchall()
                res = [lins for lins in partner_obj.browse( cr, uid, [li['id'] for li in dat], context=context )]
                print "GET_PARTNER_DETAIL %s" % res
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
