# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Hugo Adan (hugo@vauxoo.com)
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

from openerp import models, fields, api
from lxml import etree


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    qty_attachments = fields.Integer("Attachments",
                                     compute="count_attachments",
                                     store=False)

    @api.multi
    def count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        for record in self:
            record.qty_attachments = obj_attachment.search_count(
                [('res_model', '=', 'account.invoice'),
                 ('res_id', '=', record.id)])
"""
    @api.model
    def fields_view_get(self, view_id='account.invoice_tree',
                        view_type='tree', toolbar=False, submenu=False):

        context = self._context
        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'tree':
            if context.get('type') in ('in_invoice', 'in_refund'):
                res['arch'] = etree.tostring(doc)
                return res
            for node in doc.xpath("//field[@name='qty_attachments']"):
                doc.remove(node)
            res['arch'] = etree.tostring(doc)
        return res
"""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
