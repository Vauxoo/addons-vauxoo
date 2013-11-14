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

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_invoice_certificate(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        company_obj = self.pool.get('res.company')
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            context.update({'date_work': invoice.date_invoice})
            certificate_id = False
            certificate_id = company_obj._get_current_certificate(cr, uid, [
                invoice.company_emitter_id.id], context=context)[
                invoice.company_emitter_id.id]
            certificate_id = certificate_id and certificate_obj.browse(
                cr, uid, [certificate_id], context=context)[0] or False
            res[invoice.id] = certificate_id and certificate_id.id or False
        return res

    _columns = {
        'certificate_id': fields.function(_get_invoice_certificate, method=True,
            type='many2one', relation='res.company.facturae.certificate',
            string='Invoice Certificate', store=True,
            help='Id of the certificate used for the invoice'),
    }
