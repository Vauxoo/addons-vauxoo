# -*- encoding: utf-8 -*-
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

from openerp.addons.report_webkit import webkit_report
from openerp.report import report_sxw
from lxml import html


class user_story_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(user_story_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'parse_html_field': self._parse_html_field,
        })
        self.context = context

    def _parse_html_field(self, data):
        if data:
            data_str = data.encode('ascii', 'xmlcharrefreplace')
            data_str = data_str.replace('<br>', '\n')
            root = html.fromstring(data_str)
            text_data = html.tostring(root, encoding='unicode', method='text')
            text_data = text_data.encode('ascii', 'xmlcharrefreplace')
            return text_data
        return ''

webkit_report.WebKitParser('report.user.story.report',
            'user.story',
            'addons/user_story/report/user_story_report.mako',
            parser=user_story_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
