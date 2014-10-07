##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#

#
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

from openerp.report import report_sxw
from lxml import html


class story_user_html(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(story_user_html, self).__init__(
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

report_sxw.report_sxw('report.user.story.report',
            'user.story',
            'addons/user_story/report/user_story_report.sxw',
            parser=story_user_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
