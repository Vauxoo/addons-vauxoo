# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.osv import fields, osv
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class wizard_report_aged_partner_balance(osv.osv_memory):
    _name = 'wizard.report.aged.partner.balance'

    def default_get(self, cr, uid, fields_list=None, context=None):
        res = {}
        acc_ag_obj = self.pool.get('account.aged.trial.balance')
        if context.get('active_model') == 'account.aged.trial.balance':
            partners_dict = acc_ag_obj._get_partners(
                cr, uid, context.get('active_ids'),
                context.get('data'), context=context)
            partner_ids = [partner.get('id') for partner in partners_dict]
            res.update({'partner_ids_default': partner_ids,
                        'aged_trial_report_id':
                        context.get('active_id', False)})
        return res

    _columns = {
        'group_user': fields.boolean(
            'Group by User', help='¿Group report by user?'),
        'show_aml': fields.boolean(
            'Show Journal Entries', help='In the report was show the '
            'journal entries'),
        'partner_ids': fields.many2many(
            'res.partner', 'partner_in_report_aged', 'wizard_id',
            'partner_id', 'Partners', help='Partners to show in Report'),
        'partner_ids_default': fields.many2many(
            'res.partner', 'partner_in_report_aged_default',
            'wizard_id', 'partner_id', 'Partners Default',
            help='Partners to show in Report by default'),
        'aged_trial_report_id': fields.many2one('account.aged.trial.balance',)
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {'ids': ids}
        if context.get('datas', False):
            datas = context.get('datas')
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_aged_partner_balance_report',
            'datas': datas,
        }

HeaderFooterTextWebKitParser('report.account_aged_partner_balance_report',
                             'account.aged.trial.balance',
                             'account_aged_partner_balance_vw/report/'
                             'account_aged_partner_balance.mako',
                             header="external")
