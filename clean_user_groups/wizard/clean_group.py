#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID



class clean_groups(osv.TransientModel):

    _name = 'clean.groups'

    _columns = {
        'sure': fields.boolean('Sure', help="Are sure this operation"),
        'confirm': fields.boolean('Confirm', help="Are sure this operation"),
    }

    def clean_user_groups(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for wzr_brw in self.browse(cr, uid, ids, context=context):
            if wzr_brw.sure and wzr_brw.confirm:
                if context.get('active_ids') and SUPERUSER_ID not in context.get('active_ids',[]):
                    self.pool.get('res.users').write(cr, uid,
                                                     context.get('active_ids'),
                                                     {'groups_id':[(6,0,[])]},
                                                     context=context)
                    
                else:
                    raise osv.except_osv(_('Error'),
                                               _('You can"t delete groups to '
                                                 'admin user'))
            else:
                raise osv.except_osv(_('Error'),
                                               _('Please select the checkbox'))
        return {'type': 'ir.actions.act_window_close'}
