# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna Hernandez (julio@vauxoo.com)
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release


class ir_attachment_facturae_mx(osv.Model):

    _inherit = 'ir.attachment.facturae.mx'

    def signal_cancel(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(ir_attachment_facturae_mx, self).signal_cancel(cr, uid, ids)
        for att in self.browse(cr, uid, ids):
            if res and att.model_source == 'hr.payslip' and att.id_source:
                if self.pool.get(att.model_source).browse(cr, uid, att.id_source).state != 'cancel':
                    res = self.pool.get(att.model_source).cancel_sheet(
                        cr, uid, [att.id_source], context=context)
        return res
        
