# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp import api, fields, models, _
from openerp.addons.controller_report_xls.controllers.main \
    import ReportController

import base64


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def wkf_send_rfq(self):
        assert len(self) == 1, _('This option should only be used '
                                 'for a single id at a time.)')
        try:
            if self._context.get('send_rfq'):
                template = self.env.ref(
                    'purchase.email_template_edi_purchase',
                    False
                )
            else:
                template = self.env.ref(
                    'purchase.email_template_edi_purchase_done',
                    False
                )
        except ValueError:
            template = False
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form',
            False
        )
        # file ext is xls?
        check_xls = False
        # get attachment
        file_xls = self.env['ir.attachment'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', '=', self.ids[0])
        ])
        # check attachment ext
        if len(file_xls) == 1:
            check_xls = file_xls.datas_fname and \
                file_xls.datas_fname.endswith('.xls')
        if len(file_xls) > 1:
            attch_ids = [atta.id for atta in file_xls if file_xls.datas_fname
                         and file_xls.datas_fname.endswith('.xls')]
            check_xls = bool(attch_ids)
            file_xls = check_xls and attch_ids[0]
        # if not exist file xls in attachments
        if not check_xls:
            # get html from qweb report
            html = self.env['report'].get_html(
                self,
                'purchase_rfq_xls.report_template',
                data={'ids': self.ids, 'form': {}}
            )
            # convert html to xls
            xls = ReportController().get_xls(html)
            # create attachment
            file_xls = self.env['ir.attachment'].create({
                'name': 'RFQ_' + str(self.name) + '.xls',
                'datas': base64.b64encode(xls),
                'datas_fname': 'RFQ_' + str(self.name) + '.xls',
                'type': 'binary',
                'res_model': 'purchase.order',
                'res_id': self.ids[0],
                'user_id': self._uid,
            })
        # create mail
        composer = self.env['mail.compose.message'].create({
            'model': 'purchase.order',
            'res_id': self.id,
            'template_id': template.id,
            'composition_mode': 'comment',
        })
        # get email template data
        template_values = composer.onchange_template_id(
            template.id,
            'comment',
            'purchase.order',
            self.id
        )['value']
        # assign new attachment
        template_values['attachment_ids'] = [
            (4, elem) for elem in template_values.get('attachment_ids', [])
        ]
        template_values['attachment_ids'].append((4, file_xls.id))
        composer.write(template_values)

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'res_id': composer.id,
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
        }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _compute_external_id(self):
        for record in self:
            xml_id = record.get_external_id()[record.id]
            xml_id = len(xml_id) and xml_id or \
                record._BaseModel__export_xml_id()
            record.xml_id = xml_id

    @api.multi
    def _compute_vendor_code(self):
        for record in self:
            domain = [('product_tmpl_id', '=',
                       record.product_id.product_tmpl_id.id),
                      ('name', '=', record.order_id.partner_id.id)]
            supplierinf = self.env['product.supplierinfo'].search(domain)
            record.vendor_code = supplierinf.product_code

    xml_id = fields.Char(compute=_compute_external_id,
                         store=False,
                         size=128,
                         string='External ID',
                         help="ID of the view defined in xml file")

    vendor_code = fields.Char(compute=_compute_vendor_code,
                              store=False,
                              size=128,
                              string='Vendor Code',
                              help="Supplier product code")
