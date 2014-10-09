# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (fernando_ld@vauxoo.com)
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
from openerp.osv import osv

import openerp.netsvc as netsvc


class mrp_production(osv.Model):
    _inherit = "mrp.production"

    def action_cancel(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        wf_service = netsvc.LocalService("workflow")

        for production in self.browse(cr, uid, ids, context=context):
            for line in production.picking_ids:
                wf_service.trg_validate(
                    uid, 'stock.picking', line.id, 'button_cancel', cr)
        return super(mrp_production, self).action_cancel(cr, uid, ids,
                                                            context=context)
