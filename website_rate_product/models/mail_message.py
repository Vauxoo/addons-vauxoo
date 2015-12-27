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
from openerp.osv import osv, fields


class MailMessage(osv.Model):
    _inherit = 'mail.message'
    _columns = {
        'rating': fields.integer('Rating'),
    }

    def _message_read_dict(self, cr, uid, message, parent_id=False,
                           context=None):
        res = super(MailMessage, self)._message_read_dict(cr, uid,
                                                          message,
                                                          parent_id=parent_id,
                                                          context=context)
        res['rating'] = message.rating
        return res


class ProductTemplate(osv.Model):
    _inherit = 'product.template'

    def _get_rating(self, cr, uid, ids, field_name, arg, context):
        res = {}
        total = 0
        cr.commit()
        for pid in ids:
            cr.execute("select avg(rating) from mail_message where res_id = %s\
                        and model = 'product.template' and rating > 0;" %
                       (pid))
            fall = cr.fetchall()
            total = fall[0][0] if fall else total
            res[pid] = total
        return res

    def _get_message_ids(self, cr, uid, ids, context=None):
        product_ids = []
        message_obj = self.pool.get('mail.message')
        message_group = message_obj.read_group(cr, uid, [('model', '=',
                                                          'product.template'),
                                                         ('id', 'in', ids)],
                                               ('res_id'),
                                               ('res_id'))
        for message in message_group:
            product_ids.append(message.get('res_id'))
        return product_ids

    _columns = {
        'rating': fields.function(_get_rating, type="integer", method=True,
                                  string="Rating",
                                  store={'mail.message':
                                         (_get_message_ids, ['res_id',
                                                             'model'], 10)}),
    }
