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

from osv import osv
from osv import fields
from tools.translate import _
import release

class ir_sequence_approval(osv.osv):
    _name = 'ir.sequence.approval'

    _rec_name = 'approval_number'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'approval_number': fields.char(u'Numero de Aprobacion', size=64, required=True),
        'serie': fields.char(u'Serie de Folios', size=12, required=False, help="Con la que se reporto al SAT, por ejemplo. FA (para facturas), NC (Para notas de credito)"),
        'approval_year': fields.char(u'Anio de Aprobacion', size=32, required=True),
        'number_start': fields.integer(u'Desde', required=False),
        'number_end': fields.integer(u'Hasta', required=True),
        'sequence_id': fields.many2one('ir.sequence', u'Sequence', required=True, ondelete='cascade'),
        'type': fields.selection([('cfd22', 'CFD 2.2'), ('cfdi32', 'CFDI 3.2'), ('cbb', 'CBB')], 'Type', required=True),
    }

    _defaults = {
        #'serie': lambda *a: '0',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'ir.sequence.approval', context=c),
    }

    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )', 'El numero inicial (Desde), tiene que ser menor al final (Hasta)!'),
        ('number_end', 'CHECK (number_end > number_start )', 'El numero final (Hasta), tiene que ser mayor al inicial (Desde)!'),
        #('approval_number_uniq', 'UNIQUE (approval_number)', 'El numero de aprobacion tiene que ser unico'),
    ]

    def _check_numbers_range(self, cr, uid, ids, context=None):
        approval = self.browse(cr, uid, ids[0], context=context)
        query = """SELECT approval_1.id AS id1, approval_2.id AS id2--approval_1.number_start, approval_1.number_end, approval_2.number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start and approval_2.number_end )
            LIMIT 1
        """%( approval.sequence_id.id )
        cr.execute( query )
        res = cr.dictfetchone()
        if res:
            return False
        return True

    _constraints = [
        (_check_numbers_range, 'Error ! Hay rangos de numeros solapados entre aprobaciones.', ['sequence_id', 'number_start', 'number_end'])
    ]
ir_sequence_approval()


class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    def copy(self, cr, uid, id, default={}, context={}, done_list=[], local=False):
        if not default:
            default = {}
        default = default.copy()
        default['approval_ids'] = False
        return super(ir_sequence, self).copy(cr, uid, id, default, context=context)

    def _get_current_approval(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        for id in ids:
            res[id] = False
        approval_obj = self.pool.get('ir.sequence.approval')
        for sequence in self.browse(cr, uid, ids, context=context):
            number_work = context.get('number_work', None) or sequence.number_next
            approval_ids = approval_obj.search(cr, uid, [
                    ('sequence_id', '=', sequence.id),
                    ('number_start', '<=', number_work),
                    ('number_end', '>=', number_work)],
                limit=1)
            approval_id = approval_ids and approval_ids[0] or False
            res[sequence.id] = approval_id
        return res

    _columns = {
        'approval_ids': fields.one2many('ir.sequence.approval', 'sequence_id', 'Sequences'),
        'approval_id': fields.function(_get_current_approval, method=True, type='many2one', relation='ir.sequence.approval', string='Approval Current'),
        #'expiring_rate': fields.integer('Tolerancia de Advertencia', help='Tolerancia Cantidad Advertencia de Folios Aprobados por Terminarse'),
        #s'expiring'
    }

    def _check_sequence_number_diff(self, cr, uid, ids, context={}):
        #ahorita nadie manda a llamar esta funcion, ya que no existen los warnings, como tal en OpenERP.
        sequence_number_diff_rate = 10
        sequences = self.browse(cr, uid, ids, context=context)
        data = {}
        for sequence in sequences:
            if sequence.approval_id:
                sequence_number_diff = sequence.approval_id.number_end - sequence.next_number
                if sequence_number_diff <= sequence_number_diff_rate:
                    warning = {
                        'title': 'Caution sequences!',
                        'message': 'Los folios estan proximos a terminarse, del sequence %s'%( sequence.name )
                    }
                    data = {'warning': warning}
                    break
                    #raise osv.except_osv(_('Warning !'), _('You cannot remove/deactivate an account which is set as a property to any Partner!'))
        print "_check_sequence_number_diff [data]",[data]
        return data

    def get_id(self, cr, uid, sequence_id, test='id=%s', context=None):
        if context is None:
            context = {}
        if release.version < '6':
            #inicia copy & paste, de una seccion de la funcion original
            if test not in ('id=%s', 'code=%s'):
                raise ValueError('invalid test')
            cr.execute('select id from ir_sequence where '+test+' and active=%s', (sequence_id, True,))
            res = cr.dictfetchone()
            #Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [sequence.id], field_names=None, arg=False, context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise osv.except_osv('Error !', 'No hay una aprobacion valida de folios.')
                    """
                    else:
                        _validation_sequence_number_diff(self, cr, uid, ids, context={}):
                        sequence_number_diff = sequence.approval_id.number_end - sequence.next_number
                        if sequence_number_diff <= sequence_number_diff_rate:
                            #warning ya esta proximo a vencer
                            #raise osv.except_osv(_('Warning !'), _('You cannot remove/deactivate an account which is set as a property to any Partner!'))
                            pass
                    """
            #return super(ir_sequence, self).get_id(cr, uid, sequence_id, test, context=context)
            return super(ir_sequence, self).get_id(cr, uid, sequence_id, test)
        else:
            #inicia copy & paste, de una seccion de la funcion original
            if test =='id=%s':
                test = 'id'
            if test =='code=%s':
                test = 'code'
            assert test in ('code','id')
            company_id = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)['company_id'][0] or None
            cr.execute('''SELECT id, number_next, prefix, suffix, padding
                          FROM ir_sequence
                          WHERE %s=%%s
                           AND active=true
                           AND (company_id = %%s or company_id is NULL)
                          ORDER BY company_id, id
                          --FOR UPDATE NOWAIT''' % test,
                          (sequence_id, company_id))
            res = cr.dictfetchone()
            #Finaliza copy & paste, de una seccion de la funcion original
            if res:
                sequence = self.browse(cr, uid, res['id'], context=context)
                if sequence.approval_ids:
                    approval_obj = self.pool.get('ir.sequence.approval')
                    approval_id = self._get_current_approval(cr, uid, [sequence.id], field_names=None, arg=False, context=context)[sequence.id]
                    approval_id = approval_id and approval_obj.browse(cr, uid, [approval_id], context=context)[0] or False
                    if not approval_id:
                        raise osv.except_osv('Error !', 'No hay una aprobacion valida de folios.')
                    return super(ir_sequence, self).get_id(cr, uid, res['id'], 'id')
            return super(ir_sequence, self).get_id(cr, uid, sequence_id, test)
ir_sequence()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
