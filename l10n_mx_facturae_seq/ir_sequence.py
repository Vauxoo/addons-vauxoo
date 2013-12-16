# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import release


class ir_sequence_approval(osv.Model):
    _name = 'ir.sequence.approval'

    _rec_name = 'approval_number'

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = []
        return types

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where will add this approval'),
        'approval_number': fields.char(u'Approval Number', size=64,
            required=True, help='Name of the type of Electronic Invoice to \
            configure'),
        'serie': fields.char(u'Serie of Folios', size=12, required=False,
            help="With which report to SAT, example. FA (for Invoices), NC \
            (For Invoice Refund)"),
        'approval_year': fields.char('Year Approval', size=32, required=True,
            help='Year of approval from the Certificate'),
        'number_start': fields.integer(u'Since', required=False,
            help='Initial Number of folios purchased'),
        'number_end': fields.integer(u'Until', required=True,
            help='Finished Number of folios purchased'),
        'sequence_id': fields.many2one('ir.sequence', u'Sequence',
            required=True, ondelete='cascade', help='Sequence where will add \
            this approval'),
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
            required=True, help="Type of Electronic Invoice"),
    }

    _defaults = {
        #'serie': lambda *a: '0',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').\
            _company_default_get(cr, uid, 'ir.sequence.approval', context=c),
    }

    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )',
         'The initial number (Since), must be less to end (Until)!'),
        ('number_end', 'CHECK (number_end > number_start )',
         'The finished number (Until), must be higher to initial (Since)!'),
        #('approval_number_uniq', 'UNIQUE (approval_number)', 'El numero de aprobacion tiene que ser unico'),
    ]

    def _check_numbers_range(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        approval = self.browse(cr, uid, ids[0], context=context)
        query = """SELECT approval_1.id AS id1, approval_2.id AS id2--\
            approval_1.number_start, approval_1.number_end, approval_2.\
            number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id and 
               approval_2.company_id = approval_1.company_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start \
                and approval_2.number_end )
            LIMIT 1
        """ % ( approval.sequence_id.id )
        cr.execute(query)
        res = cr.dictfetchone()
        if res:
            return False
        return True

    _constraints = [
        (_check_numbers_range, 'Error ! There ranges of numbers underhand between approvals.',\
            ['sequence_id', 'number_start', 'number_end', 'company_id'])
    ]


class ir_sequence(osv.Model):
    _inherit = 'ir.sequence'

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        if context is None:
            context = {}
        if not default:
            default = {}
        default = default.copy()
        default['approval_ids'] = False
        return super(ir_sequence, self).copy(cr, uid, id, default, context=context)

    def _get_current_approval(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = False
        approval_obj = self.pool.get('ir.sequence.approval')
        for sequence in self.browse(cr, uid, ids, context=context):
            number_work = sequence.number_next_actual or False
            number_work = number_work-1
            approval_ids = approval_obj.search(cr, uid, [
                ('sequence_id', '=', sequence.id),
                ('number_start', '<=', number_work),
                ('number_end', '>=', number_work),
                ('company_id', '=', sequence.company_id.id)],
                limit=1)
            approval_id = approval_ids and approval_ids[0] or False
            res[sequence.id] = approval_id
        return res

    _columns = {
        'approval_ids': fields.one2many('ir.sequence.approval', 'sequence_id',
            'Sequences', help='Approvals in this Sequence'),
        'approval_id': fields.function(_get_current_approval, method=True,
            type='many2one', relation='ir.sequence.approval',
            string='Approval Current', help='Approval active in this sequence'),
        #'expiring_rate': fields.integer('Tolerancia de Advertencia', help='Tolerancia Cantidad Advertencia de Folios Aprobados por Terminarse'),
        # s'expiring'
    }

    def _check_sequence_number_diff(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        # ahorita nadie manda a llamar esta funcion, ya que no existen los
        # warnings, como tal en OpenERP.
        sequence_number_diff_rate = 10
        sequences = self.browse(cr, uid, ids, context=context)
        data = {}
        for sequence in sequences:
            if sequence.approval_id:
                sequence_number_diff = sequence.approval_id.number_end - \
                    sequence.next_number
                if sequence_number_diff <= sequence_number_diff_rate:
                    warning = {
                        'title': 'Caution sequences!',
                        'message': 'The folios are close to finish, of the sequence %s' % (
                            sequence.name)
                    }
                    data = {'warning': warning}
                    break
                    # raise osv.except_osv(_('Warning !'), _('You cannot
                    # remove/deactivate an account which is set as a property
                    # to any Partner!'))
        print "_check_sequence_number_diff [data]", [data]
        return data

    def get_id(self, cr, uid, sequence_id, test='id=%s', context=None):
        if context is None:
            context = {}
        if release.version < '6':
            # inicia copy & paste, de una seccion de la funcion original
            if test not in ('id=%s', 'code=%s'):
                raise ValueError('invalid test')
            cr.execute('select id from ir_sequence where '+test+' and active=%s', (
                sequence_id, True,))
            res = cr.dictfetchone()
            # Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [
                        sequence.id], field_names=None, arg=False,
                        context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(
                        cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise osv.except_osv(
                            'Error !', 'No hay una aprobacion valida de folios.')
                    """
                    else:
                        _validation_sequence_number_diff(self, cr, uid, ids,
                            context=context):
                        sequence_number_diff = sequence.approval_id.number_end \
                            - sequence.next_number
                        if sequence_number_diff <= sequence_number_diff_rate:
                            #warning ya esta proximo a vencer
                            #raise osv.except_osv(_('Warning !'), _('You \
                                cannot remove/deactivate an account which is \
                                set as a property to any Partner!'))
                            pass
                    """
            # return super(ir_sequence, self).get_id(cr, uid, sequence_id,
            # test, context=context)
            return super(ir_sequence, self).get_id(cr, uid, sequence_id, test)
        else:
            # inicia copy & paste, de una seccion de la funcion original
            if test == 'id=%s':
                test = 'id'
            if test == 'code=%s':
                test = 'code'
            assert test in ('code', 'id')
            company_id = self.pool.get('res.users').read(cr, uid, uid, [
                'company_id'], context=context)['company_id'][0] or None
            cr.execute('''SELECT id, number_next, prefix, suffix, padding
                          FROM ir_sequence
                          WHERE %s=%%s
                           AND active=true
                           AND (company_id = %%s or company_id is NULL)
                          ORDER BY company_id, id
                          --FOR UPDATE NOWAIT''' % test,
                      (sequence_id, company_id))
            res = cr.dictfetchone()
            # Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [
                        sequence.id], field_names=None, arg=False,
                        context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(
                        cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise osv.except_osv(
                            'Error !', 'No hay una aprobacion valida de folios.')
                    return super(ir_sequence, self).get_id(cr, uid, res['id'], 'id')
            return super(ir_sequence, self).get_id(cr, uid, sequence_id, test)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
