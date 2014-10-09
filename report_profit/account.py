# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import osv


class account_move_line(osv.Model):
    _inherit = 'account.move.line'
    _description = "Entry lines"

    def find(self, cr, uid, **kwargs):
        res = []
        cond_str = ''
        cond_val = []

        if kwargs.get('dt', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.date=%s'
            cond_val.append(kwargs['dt'])
        if kwargs.get('acc_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.account_id=%s'
            cond_val.append(kwargs['acc_id'])
        if kwargs.get('prd_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.product_id=%s'
            cond_val.append(kwargs['prd_id'])
        if kwargs.get('mov_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.move_id=%s'
            cond_val.append(kwargs['mov_id'])
        if kwargs.get('per_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.period_id=%s'
            cond_val.append(kwargs['per_id'])
        if kwargs.get('jou_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.journal_id=%s'
            cond_val.append(kwargs['jou_id'])
        if kwargs.get('par_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.partner_id=%s'
            cond_val.append(kwargs['par_id'])
        if kwargs.get('cur_id', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.currency_id=%s'
            cond_val.append(kwargs['cur_id'])
        if kwargs.get('qty', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.quantity=%s'
            cond_val.append(kwargs['qty'])
        if kwargs.get('name', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.name=%s'
            cond_val.append(kwargs['name'])
        if kwargs.get('ref', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.ref=%s'
            cond_val.append(kwargs['ref'])
        if kwargs.get('debit', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.debit=%s'
            cond_val.append(kwargs['debit'])
        if kwargs.get('credit', False):
            if cond_str:
                cond_str += ' AND '
            cond_str += 'aml.credit=%s'
            cond_val.append(kwargs['credit'])

        if cond_str:
            cond_str = ' WHERE ' + cond_str

#        print 'xxxxcondicion: ',cond_str

        sql = 'SELECT aml.id FROM account_move_line aml' + \
            cond_str % tuple(cond_val)
#        print 'xxxxsql: ',sql
        cr.execute(sql)
        res = map(lambda x: x[0], cr.fetchall())

        if not res:
            return False
        return res

