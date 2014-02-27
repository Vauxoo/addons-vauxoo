# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _


class ir_sequence(osv.Model):
    """
    Ir sequence inherit to assing secuence by company
    """

    _inherit = 'ir.sequence'

#marca error al abrir una orden de produccion
#TODO: funcion _process no existe desde version 6, metodo parecido en
#ir.sequence _interpolation_dict(self), adaptar a esta funcion
"""
    def get_id(self, cr, uid, sequence_id, test='id', context=None):
        assert test in ('code', 'id')
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, 'ir.sequence', context=context)
        cr.execute('''SELECT id, number_next, prefix, suffix, padding
                      FROM ir_sequence
                      WHERE %s='%s'
                       AND active=true
                       AND company_id=%d
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % (test, sequence_id, company_id))
        res = cr.dictfetchone()

        if res:
            cr.execute('UPDATE ir_sequence\
                    SET number_next=number_next+number_increment\
                    WHERE id=%s AND active=true', (
                res['id'],))
            if res['number_next']:
                return self._process(res['prefix']) + '%%0%sd' %\
                    res['padding'] % res['number_next'] +\
                    self._process(res['suffix'])
            else:
                return self._process(res['prefix']) +\
                    self._process(res['suffix'])
        return False
"""