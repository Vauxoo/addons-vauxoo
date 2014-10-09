#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


from openerp.osv import osv
from openerp import SUPERUSER_ID


class mail_compose_message(osv.TransientModel):

    _inherit = 'mail.compose.message'

    def generate_email_for_composer(self, cr, uid, template_id, res_id, context=None):

        values = super(mail_compose_message, self).generate_email_for_composer(cr, uid,
                                                        template_id, res_id, context=context)

        email_template_obj = self.pool.get('email.template')

        email_template = email_template_obj.browse(cr, uid, template_id, context=context)
        if values.get('partner_ids', False) and email_template.add_followers:
            partners_to_notify = set([])
            partner_follower = self.pool.get('mail.followers')

            fol_ids = partner_follower.search(cr, SUPERUSER_ID, [
                ('res_model', '=', context.get('active_model')),
                ('res_id', '=', context.get('active_id')),
            ], context=context)

            partners_to_notify |= set(fo.partner_id.id
                    for fo in partner_follower.browse(cr, SUPERUSER_ID, fol_ids, context=context))

            partners_followers_notify = values.get('partner_ids', []) + list(partners_to_notify)
            values.update({'partner_ids': list(set(partners_followers_notify))})
        return values
