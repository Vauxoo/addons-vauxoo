# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Maria Gabriela Quilarque)
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountInvoice(osv.osv):

    _inherit = 'account.invoice'

    _columns = {
        'to_pay': fields.boolean('To Pay', readonly=True, help="This field will be marked when the purchase manager approve this invoice to be paid, and unmarked if the invoice will be blocked to pay"),
    }
    _defaults = {
        'to_pay': False,
    }

    @api.one
    def copy(self, default=None):
        default = default or {}
        default.update({
            'to_pay': False,
        })
        return super(AccountInvoice, self).copy(default)

    def payment_approve(self, cr, uid, ids, context=None):
        """Mark boolean as True, to approve invoice to be pay.
        Added message to messaging block of supplier invoice,
        when approve invoice.
        """
        context = context or {}

        context.update({'default_body': _(u'Invoice Approved to Pay'),
                        'default_parent_id': False,
                        'mail_post_autofollow_partner_ids': [],
                        'default_attachment_ids': [],
                        'mail_post_autofollow': True,
                        'default_composition_mode': '',
                        'default_partner_ids': [],
                        'default_model': 'account.invoice',
                        'active_model': 'account.invoice',
                        'default_res_id': ids and type(ids) is list and
                        ids[0] or ids,
                        'active_id': ids and type(ids) is list and
                        ids[0] or ids,
                        'active_ids': ids and type(ids) is list and
                        ids or [ids],
                        'stop': True,
                        })

        mail_obj = self.pool.get('mail.compose.message')
        fields = mail_obj.fields_get(cr, uid)
        mail_dict = mail_obj.default_get(cr, uid, fields.keys(), context)
        mail_ids = mail_obj.create(cr, uid, mail_dict, context=context)
        mail_obj.send_mail(cr, uid, [mail_ids], context=context)

        return self.write(cr, uid, ids, {'to_pay': True})

    def payment_disapproves(self, cr, uid, ids, context=None):
        """Mark boolean as False, to Disapprove invoice to be pay.
        Added message to messaging block of supplier invoice,
        when disapproved to Pay.
        """
        context = context or {}

        context.update({'default_body': _(u'Invoice Disapproved to Pay'),
                        'default_parent_id': False,
                        'mail_post_autofollow_partner_ids': [],
                        'default_attachment_ids': [],
                        'mail_post_autofollow': True,
                        'default_composition_mode': '',
                        'default_partner_ids': [],
                        'default_model': 'account.invoice',
                        'active_model': 'account.invoice',
                        'default_res_id': ids and type(ids) is list and
                        ids[0] or ids,
                        'active_id': ids and type(ids) is list and
                        ids[0] or ids,
                        'active_ids': ids and type(ids) is list and
                        ids or [ids],
                        'stop': True,
                        })

        mail_obj = self.pool.get('mail.compose.message')
        fields = mail_obj.fields_get(cr, uid)
        mail_dict = mail_obj.default_get(cr, uid, fields.keys(), context)
        mail_ids = mail_obj.create(cr, uid, mail_dict, context=context)
        mail_obj.send_mail(cr, uid, [mail_ids], context=context)

        return self.write(cr, uid, ids, {'to_pay': False})
