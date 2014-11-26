# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral      <kathy@vauxoo.com>
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


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'batch_type': fields.selection(
            [('bottleneck', 'Avoid Production Bottleneck'),
             ('max_cost', 'Maxime Workcenter Productivity / Minimizing Production Cost')],
            'Production Batch Process Type',
            help=('Two options when management the batch work orders:\n\n'
                  ' - Avoid Production Bottleneck: Will create the batch'
                  ' work orders taking into a count the minium workcenter'
                  ' capacity.'
                  ' - Maxime Workcenter Productivity / Minimizing Production'
                  ' Cost: For every workcenter will'
                  ' create a batch of works orders that always explotes the'
                  ' product capacity of the workcenter.\n')
        ),
    }

    _defaults = {
        'batch_type': 'bottleneck',
    }
