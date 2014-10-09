# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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

from openerp.osv import osv, fields
from lxml import etree
import openerp.tools as tools


class account_move_line(osv.Model):
    _inherit = 'account.move.line'
    _columns = {
        'address_id': fields.many2one('res.partner.address', 'Address', domain="[('partner_id','=',partner_id)]")
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(account_move_line, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        fields_get = self.fields_get(cr, uid, ['address_id'], context)
        xml_form = etree.fromstring(result['arch'])
        placeholder = xml_form.xpath("//field[@name='partner_id']")
        placeholder[0].addnext(etree.Element('field', {'name': 'address_id'}))
        result['arch'] = etree.tostring(xml_form)
        result[
            'fields'].update({'address_id': {'domain': [], 'string': u'Sucursal', 'readonly': False,
                                             'relation': 'res.partner.address', 'context': {}, 'selectable': True, 'type': 'many2one', 'select': 2}})
        return result


class account_entries_report(osv.Model):
    _inherit = 'account.entries.report'
    _columns = {
        'address_id': fields.many2one('res.partner.address', 'Address')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_entries_report')
        cr.execute("""
            create or replace view account_entries_report as (
            select
                l.id as id,
                am.date as date,
                l.date_maturity as date_maturity,
                l.date_created as date_created,
                am.ref as ref,
                am.state as move_state,
                l.state as move_line_state,
                l.reconcile_id as reconcile_id,
                to_char(am.date, 'YYYY') as year,
                to_char(am.date, 'MM') as month,
                to_char(am.date, 'YYYY-MM-DD') as day,
                l.partner_id as partner_id,
                l.product_id as product_id,
                l.product_uom_id as product_uom_id,
                am.company_id as company_id,
                am.journal_id as journal_id,
                p.fiscalyear_id as fiscalyear_id,
                am.period_id as period_id,
                l.account_id as account_id,
                l.analytic_account_id as analytic_account_id,
                a.type as type,
                a.user_type as user_type,
                1 as nbr,
                l.quantity as quantity,
                l.currency_id as currency_id,
                l.amount_currency as amount_currency,
                l.debit as debit,
                l.credit as credit,
                l.debit-l.credit as balance,
                l.address_id as address_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
                where l.state != 'draft'
            )
        """)
