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


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    qty_attachments = fields.Integer("Attachments",
                                     help='Number of attachments per invoice',
                                     compute="count_attachments",
                                     store=False)

    @api.one
    def count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        self.qty_attachments = obj_attachment.search_count(
            [('res_model', '=', 'account.invoice'),
             ('res_id', '=', self.id,)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
