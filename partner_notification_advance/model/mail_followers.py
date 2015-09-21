# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
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
#
from openerp.osv import osv


class MailNotification(osv.Model):

    _inherit = 'mail.notification'

    def get_partners_to_email(self, cr, uid, ids, message, context=None):
        """ Return the list of partners to notify, based on their preferences.
            :param browse_record message: mail.message to notify
            :param list partners_to_notify: optional list of partner ids
            restricting the notifications to process
        """
        notify_pids = []
        for notification in self.browse(cr, uid, ids, context=context):
            if notification.is_read:
                continue
            partner = notification.partner_id
            # Do not send to partners without email address defined
            if not partner.email:
                continue
            # Do not send to partners having same email address than the
            # author (can cause loops or bounce effect due to messy database)
            if message.author_id and message.author_id.email == partner.email:
                continue
            # Partner does not want to receive any emails or is opt-out
            if partner.notify_email == 'none':
                continue
            # Partner wants to receive only emails and comments
            if partner.notify_email == 'comment' and message.type not in (
                    'email', 'comment'):
                continue
            # Partner wants to receive only emails
            if partner.notify_email == 'email' and message.type != 'email':
                continue
            notify_pids.append(partner.id)
        return notify_pids
