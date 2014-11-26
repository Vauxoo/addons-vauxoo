# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
##########################################################################

from openerp.osv import osv
from lxml import etree


class account_move_line(osv.Model):
    _inherit = 'account.move.line'
    _columns = {

    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(account_move_line, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar,
            submenu=submenu)
        # fields_get = self.fields_get(cr, uid, ['stock_move_id'], context)
        xml_form = etree.fromstring(result['arch'])
        placeholder = xml_form.xpath("//field[@name='period_id']")
        placeholder[0].addnext(etree.Element('field', {'name': 'product_id'}))
        result['arch'] = etree.tostring(xml_form)
        result['fields'].update({
            'product_id': {
                'domain': [],
                'string': u'Product',
                'readonly': False,
                'relation': 'product.product',
                'context': {},
                'selectable': True,
                'type': 'many2one',
                'select': 2}
        })
        return result
