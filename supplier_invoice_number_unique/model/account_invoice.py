# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##########################################################################
#    Coded by: Luis Ernesto García Medina(ernesto_gm@vauxoo.com)
# ##############Credits#####################################################
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
# ##########################################################################
from openerp import models, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_validate_ref_invoice(self):
        for invoice in self:
            if invoice.supplier_invoice_number:
                self._cr.execute(
                    """
                    SELECT supplier_invoice_number,
                        lower(regexp_replace(
                            supplier_invoice_number, """ + r"'\W" + """+', '',
                            'g')) AS data
                    FROM account_invoice ai JOIN res_partner rp
                        ON ai.partner_id = rp.id
                    WHERE lower(regexp_replace(
                        supplier_invoice_number, """ + r"'\W" + """+', '',
                            'g')) = lower(
                            regexp_replace(%s, """ + r"'\W" + """+', '', 'g'))
                    AND ai.id != %s
                    AND rp.commercial_partner_id = %s
                    AND state not in ('draft', 'cancel')
                    AND ai.company_id = %s
                    """, (
                        invoice.supplier_invoice_number,
                        invoice.id,
                        invoice.partner_id.commercial_partner_id.id,
                        invoice.company_id.id)
                )
                invoice_duplicate_ids = self._cr.fetchall()
                if invoice_duplicate_ids:
                    raise UserError(
                        _('Invalid Action!'),
                        _(
                            'Error you can not validate the invoice with '
                            'supplier invoice number duplicated.'))
        return True

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            invoice.action_validate_ref_invoice()
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'supplier_invoice_number': False})
        return super(AccountInvoice, self).copy(default)
