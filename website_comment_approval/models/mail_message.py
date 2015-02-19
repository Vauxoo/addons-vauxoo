# -*- coding:utf-8 -*-
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
from openerp.osv import osv


class mail_message(osv.Model):
    _inherit = 'mail.message'
    _defaults = {
        'website_published': False,
    }

    def _message_read_dict(self, cr, uid, message, parent_id=False,
                           context=None):
        r = super(mail_message, self)._message_read_dict(cr, uid,
                                                         message,
                                                         parent_id=parent_id,
                                                         context=context)
        r['website_published'] = message.website_published
        return r
