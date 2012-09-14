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
ifrs_lines()

class ifrs_lines(osv.osv):

    _inherit = 'ifrs.lines'
    _parent_store = True


    #~ def _get_ifrls_with_total_ids_updated(self, cr, uid, ids, field_name, arg, context = None):
        #~ if context is None: context = {}
        #~ res = {}
#~
        #~ print '\n IDS de _get_total_ids_updated'
        #~ print ids
        #~ return res
#~
    #~ def _get_parent_id(self, cr, uid, ids, field_name, arg, context = None):
        #~ if context is None: context = {}
        #~ res = {}

        #~ for ifrs_l in ids:
            #~ for ifrsl_child in ifrs_l.total_ids
                #~ res = {}
                #~ if 'abstract' not in ifrsl_child.type
                    #~ res[ifrs_l]=
                    #~ cr.execute( 'select * from ifrs_lines_rel where parent_id=%s', (ifrs_) )
                    #~ print cr.fetchone()
        #~ return res

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
        return res

    def _consolidated_accounts_sum( self, cr, uid, ids, field_name, arg, context = None ):
        if context is None: context = {}
        res = {}
        for id in ids:
            res[id] = self._get_sum( cr, uid, id, context = context )
        return res

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
        'cons_ids' : fields.many2many('account.account', 'ifrs_account_rel', 'ifrs_lines_id', 'account_id', string='Consolidated Accounts' ),
        'ifrs_id' : fields.many2one('ifrs.ifrs', 'IFRS', required = True ),
        'amount' : fields.function( _consolidated_accounts_sum, method = True, type='float', string='Amount', store=True),
        'total_ids' : fields.many2many('ifrs.lines','ifrs_lines_rel','parent_id','child_id',string='Total'),

        #~ # original
        'parent_id' : fields.many2one('ifrs.lines','Parent', ondelete ='set null'),

        #~ nueva version: campo funcional (tipo m2o), grabable y escribible
        #~ 'parent_id' : fields.function(
            #~ _get_parent_id,
            #~ method=True,
            #~ type='many2one',
            #~ relation='ifrs.lines',
            #~ store={
                #~ 'ifrs_lines' : (_get_ifrls_with_total_ids_updated, ['total_ids'], 15),
            #~ },
            #~ string='Parent' ),

        'parent_right' : fields.integer('Parent Right', select=1 ),
        'parent_left' : fields.integer('Parent Left', select=1 ),
    }

    _defaults = {
        'type' : 'abstract',
    }

    _sql_constraints = [('sequence_ifrs_id_unique','unique(sequence,ifrs_id)', 'The sequence already have been set in another IFRS line')]

ifrs_lines()

#~ pregunta. comprobacion de la linea... lo hace cuando le da a guardar--- no lo hace a la hora de ingresarlo, puede taer confuciones a la hora que el usuario agregue a mucha gente y luego no sepa a cual se refiere.

#~ buscar, como hacer para que ordene por secuencia, lo que ingreso!
