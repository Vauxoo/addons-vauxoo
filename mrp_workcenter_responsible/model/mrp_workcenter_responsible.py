# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <katherine.zaoral@vauxoo.com>
#    Planified by: Katherine Zaoral      <katherine.zaoral@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields


class mrp_workcenter(osv.Model):

    _inherit = 'mrp.workcenter'
    _columns = {
        'responsible_id': fields.many2one(
            'hr.employee',
            string='Responsible',
            help='Responsible person to perform the work center activities.'),
    }


class mrp_production_workcenter_line(osv.Model):

    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'responsible_id': fields.related(
            'workcenter_id', 'responsible_id',
            type='many2one',
            relation='hr.employee',
            readonly=True,
            string='Responsible',
            help=('Responsible person to carry out the work order. The'
                  ' responsible is the one for the work center associated.'
                  ' To change the responsible you need to change the work'
                  ' center responsible.')),
    }
