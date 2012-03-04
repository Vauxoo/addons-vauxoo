# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2011 OpenERP s.a. (<http://openerp.com>).
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

import openobject.templating

class BaseTemplateEditor(openobject.templating.TemplateEditor):
    templates = ['/openobject/controllers/templates/base.mako']

    def edit(self, template, template_text):
        output = super(BaseTemplateEditor, self).edit(template, template_text)

        end_head = output.index('</head>')

        output = output[:end_head] + """
	<link rel="stylesheet" type="text/css" href="/web_multilogo/static/css/${rpc.session.db}-multi.css"/>
        """ + output[end_head:]

        return output


class HeaderTemplateEditor(openobject.templating.TemplateEditor):
    templates = ['/openerp/controllers/templates/header.mako']


    def edit(self, template, template_text):
        output = super(HeaderTemplateEditor, self).edit(template, template_text)

        PATTERN = '<div id="corner">'
        corner = output.index(PATTERN) + len(PATTERN)


        output = output[:corner] + """
            <p id="livechat_status" class="logout">
               <a href="http://vauxoo.com">
                 ${rpc.session.db}
               </a>
            </p>
        """ + output[corner:]
        return output

