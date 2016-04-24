# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv
from openerp import SUPERUSER_ID


class ForwardMail(osv.osv_memory):

    _name = 'forward.mail'

    def action_forward_mail(self, cr, uid, ids, context=None):
        mail_pool = self.pool.get('mail.mail')
        if context is None:
            context = {}
        for mail in mail_pool.browse(cr,
                                     uid,
                                     context.get('active_ids', []),
                                     context=context):
            if mail.state == 'exception' and mail.type in ("email", "comment"):
                mail_pool.mark_outgoing(cr, uid, mail.id, context=context)
                partners_to_notify = set([])
                partner_follower = self.pool.get('mail.followers')

                fol_ids = partner_follower.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', mail.model),
                    ('res_id', '=', mail.res_id),
                ], context=context)

                partners_to_notify |= set(
                    fo.partner_id.id for fo in partner_follower.browse(
                        cr,
                        SUPERUSER_ID,
                        fol_ids,
                        context=context) if fo.partner_id.email)
                mail_pool.send(
                    cr,
                    uid,
                    [mail.id],
                    recipient_ids=partners_to_notify,
                    context=context)

        return True
