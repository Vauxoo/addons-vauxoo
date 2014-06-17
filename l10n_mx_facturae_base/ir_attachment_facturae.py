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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc


class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def signal_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        invoice_obj = self.pool.get('account.invoice')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attach = False
        for att in self.browse(cr, uid, ids, context):
            if att.model_source == 'account.invoice':
                state_invoice = invoice_obj.browse(cr, uid, [att.id_source], context=context)[0].state
                if state_invoice != 'cancel':
                    wf_service.trg_validate(uid, att.model_source, att.id_source, 'invoice_cancel', cr)
                else:
                    attach = super(ir_attachment_facturae_mx, self).signal_cancel(cr, uid, ids, context)
            else:
                attach = super(ir_attachment_facturae_mx, self).signal_cancel(cr, uid, ids, context)
        return attach
