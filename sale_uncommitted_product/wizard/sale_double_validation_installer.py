# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
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
##########################################################################


from openerp.osv import osv, fields


class sale_double_validation_installer(osv.TransientModel):
    _name = 'sale.double.validation.installer'
    _inherit = 'res.config'
    _columns = {
        'force_commit_group_id': fields.many2one('res.groups', 'Force Commit Group', required=False,
        help='''Setting this field to a group will only allow to that group to make Commitment Sale Orders without checking if complying with contraints.
        Leave blank to allow any group to force to'''),
        'commit_group_id': fields.many2one('res.groups', 'Commit Group', required=False,
        help='''Setting this field to a group will only allow to that group to make Commitment Sale Orders checking if complying with contraints.
        Leave blank to allow any group to commit to'''),
        'group_id': fields.many2one('res.groups', 'Approval Group', required=False,
        help='''Setting this field to a group will only allow to that group to approve Sale Orders.
        Leave blank to allow any group to approve to'''),
    }

    _defaults = {
        'group_id': False,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)

        force_commit_group_id = data and data[
            0]['force_commit_group_id'] or False
        commit_group_id = data and data[0]['commit_group_id'] or False
        group_id = data and data[0]['group_id'] or False

        data_pool = self.pool.get('ir.model.data')
        transition_obj = self.pool.get('workflow.transition')

        force = data_pool._get_id(
            cr, uid, 'sale_uncommitted_product', 'trans_draft_force_commit')
        force_id = data_pool.browse(cr, uid, force, context=context).res_id
        transition_obj.write(cr, uid, force_id, {
                             'group_id': force_commit_group_id})

        commit = data_pool._get_id(
            cr, uid, 'sale_uncommitted_product', 'trans_draft_commit')
        commit_id = data_pool.browse(cr, uid, commit, context=context).res_id
        transition_obj.write(cr, uid, commit_id, {'group_id': commit_group_id})

        approval = data_pool._get_id(cr, uid, 'sale', 'trans_draft_router')
        approval_id = data_pool.browse(
            cr, uid, approval, context=context).res_id
        transition_obj.write(cr, uid, approval_id, {'group_id': group_id})

        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
