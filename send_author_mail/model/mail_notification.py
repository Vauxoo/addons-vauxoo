# coding: utf-8
###########################################################################
#   Module Writen to OpenERP, Open Source Management Solution
#   Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#   All Rights Reserved
# ##############Credits######################################################
#   Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


from openerp.osv import osv


class MailNotification(osv.Model):

    _inherit = 'mail.notification'

    def get_partners_to_email(self, cr, uid, ids, message, context=None):
        """
            Overwrite this method to allow receive your own message sent
            validating the field @receive_my_emails added in model of partner
        """
        res = super(MailNotification, self).get_partners_to_email(
            cr, uid, ids, message, context=context)

        for element in self.browse(cr, uid, ids, context=context):
            if message.author_id and\
                (message.author_id.receive_my_emails and
                    message.author_id.notify_email != "none"):
                res.append(message.author_id.id)
        return res
