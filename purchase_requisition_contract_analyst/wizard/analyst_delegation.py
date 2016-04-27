# coding: utf-8

"""Wizard definition for the bdp Odoo module.
"""

###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Yanina Aular <yani@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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
from openerp.tools.translate import _


class PurchaseRequisitionAnalystDelegation(osv.TransientModel):

    """This wizard permit to delegate a authority given the user the change to
    select the employee that will have the delegation.
    """
    _name = 'purchase.requisition.analyst.delegation'
    _description = 'Purchase Requisition Analyst Delegation'
    _columns = {
        'purchaser_id': fields.many2one(
            'res.users',
            'Delegate to Analyst',
            help='This user will be in charge of the Requisition')
    }

    def delegate(self, cur, uid, ids, context=None):
        """@return True
        """
        context = context or {}
        pr_obj = self.pool.get('purchase.requisition')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        pr_ids = context.get('active_ids', False)
        wzd_brw = self.browse(cur, uid, ids[0], context=context)
        for pr_brw in pr_obj.browse(cur, uid, pr_ids, context=context):
            pr_brw.write({'purchaser_id': wzd_brw.purchaser_id.id},
                         context=context)
        return True
