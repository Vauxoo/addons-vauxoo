# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
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
import time
import datetime
from email import utils
from openerp import models, fields, api


class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.multi
    def _get_date(self):
        posts = self
        for post in posts:
            date_obj = time.strptime(post.write_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(date_obj))
            write_tuple = dt.timetuple()
            timestamp = time.mktime(write_tuple)
            post.date_rfc2822 = utils.formatdate(timestamp)

    date_rfc2822 = fields.Char(
        compute=_get_date,
        string="Date RFC-2822")
