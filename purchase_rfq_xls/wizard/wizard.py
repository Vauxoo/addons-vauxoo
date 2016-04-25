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
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError
import base64

import logging
_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.info('You have purchase_rfq_xls from '
                 'addons-vauxoo declared in your '
                 'system you will need xlrd library '
                 'in order to use this module')


class PurchaseQuotationWizard(models.TransientModel):
    _description = 'Purchase Quotation'
    _name = 'purchase.quotation.wizard'

    report_format = fields.Selection([
        ('pdf', "PDF"),
        ('xls', "Spreadsheet"),
    ], default='xls')
    template_action = fields.Selection([
        ('export', "Get a quotation template without prices"),
        ('import', "Update a quotation prices"),
    ], default='import')
    xls_file = fields.Binary("Upload template")
    xls_name = fields.Char()
    state = fields.Selection([('form', 'form'),
                              ('success', 'success'),
                              ('success2', 'success2')], default='form')
    lines_ids = fields.One2many(
        'purchase.quotation.wizard.line', 'wizard_id')

    @api.multi
    @api.constrains('xls_name')
    def _check_xls(self):
        if self.template_action == 'import' and self.xls_file:
            if not self.xls_name:
                raise ValidationError(_("There is no file"))
            else:
                if not self.xls_name.endswith('.xls'):
                    raise ValidationError(_("The file must be a xls file"))

    @api.model
    def _update_price(self, order_line, price, qty):
        data = {}
        if type(price) == type(qty) == float:
            if order_line.product_qty <= qty:
                data['price_unit'] = price
            else:
                data.update({'price_unit': price, 'product_qty': qty})
            return order_line.write(data)
        return False

    @api.model
    def get_xls_eof(self, sheet):
        """Search for the last row of a Spreadsheet
        @return: return int
        """
        row = 0
        while True:
            try:
                sheet.cell_value(row, 0)
                row += 1
            except:
                break
        return row

    @api.multi
    def import_xls(self):
        """Validate and read xls file to update quotation
        """
        context = dict(self._context)
        fdata = self.xls_file
        fname = '/tmp/%s' % (self.xls_name)
        f = open(fname, 'w')
        f.write(base64.b64decode(fdata))
        f.close()
        doc = xlrd.open_workbook(fname)
        sheet = doc.sheet_by_index(0)
        purchase = self.env['purchase.order'].browse(
            context['active_ids'])[0]
        # validate template format
        if sheet.cell_type(2, 5) not in \
                (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) and \
                sheet.cell_value(2, 5) != purchase.name:
            raise UserError(' '.join([
                _('Is not a valid template for Quotation'),
                str(purchase.name)]))
        eof = self.get_xls_eof(sheet)
        # First col header on Qweb report: template.xml
        col_start = "External ID"
        can_start = False
        done_ids = []
        new_products = []
        for row in range(eof):
            if not can_start:
                if col_start == sheet.cell_value(row, 0):
                    can_start = True
                continue
            # External ID
            xml_id = sheet.cell_value(row, 0)
            # Vendor Code
            vendor_code = sheet.cell_value(row, 2)
            # Description
            description = sheet.cell_value(row, 3)
            # Qty
            product_qty = sheet.cell_value(row, 4)
            # Cost
            price_unit = sheet.cell_value(row, 5)
            # check xml reference
            try:
                order_line = self.env.ref(xml_id)
                if self._update_price(order_line, price_unit, product_qty):
                    done_ids.append(order_line.id)
            except:
                new_products.append((0, 0, {
                    'description': description,
                    'vendor_code': vendor_code,
                    'cost': price_unit,
                }))

        if done_ids:
            order_line_done = self.env['purchase.order.line'].browse(done_ids)
            # intersect objects and unlink diff
            order_line_diff = purchase.order_line - order_line_done
            order_line_diff.unlink()
        else:
            raise UserError(
                _('Nothing to update! Probably not has product cost defined '
                  'in template'))
        if new_products:
            self.write({'state': 'success', 'lines_ids': new_products})
        else:
            self.write({'state': 'success2'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.quotation.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def print_report(self):
        """Print the report
        @return : return report
        """
        ctx = dict(self._context)
        ctx['xls_report'] = self.report_format == 'xls'
        purchase = self.env['purchase.order'].browse(ctx['active_ids'])[0]
        return self.env['report'].with_context(ctx).get_action(
            purchase,
            'purchase_rfq_xls.report_template',
            data={'ids': purchase.id})


class PurchaseQuotationWizardLine(models.TransientModel):
    _description = 'Purchase Quotation Details'
    _name = 'purchase.quotation.wizard.line'

    description = fields.Char()
    vendor_code = fields.Char()
    wizard_id = fields.Many2one('purchase.quotation.wizard')
    cost = fields.Float()
