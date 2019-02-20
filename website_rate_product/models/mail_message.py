# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala <oscar@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class MailMessage(models.Model):
    _inherit = 'mail.message'
    rating = fields.Integer('Rating')

    @api.model
    def _message_read_dict(self, message, parent_id=False):
        res = super(MailMessage, self)._message_read_dict(message,
                                                          parent_id=parent_id)
        res['rating'] = message.rating
        return res

    @api.model
    def _get_product_comments_qty(self, product_id):
        mail = self.env['mail.message']
        message_qty = mail.search_count([('res_id', '=', int(product_id)),
                                         ('website_published', '=', True),
                                         ('model', '=', 'product.template'),
                                         ('message_type', '=', 'comment')])
        return message_qty


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends("message_last_post")
    def _get_rating(self):
        """This method gets the rating for each rated template based on the
        comments, the rating per comment is stored in the mail.message model
        """
        self._cr.execute("""
            SELECT res_id, avg(rating)
            FROM mail_message
            WHERE res_id IN %s AND model = 'product.template' AND rating > 0
            GROUP BY res_id""", (self._ids,))
        res = dict(self._cr.fetchall())
        for record in self:
            record.rating = res.get(record.id)

    rating = fields.Integer(compute="_get_rating", string="Rating", store=True)
