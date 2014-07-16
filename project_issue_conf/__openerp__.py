# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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
{
    "name" : "Project Issue Conf",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Generic",
    "description" : """
    
    This module add data to configurate incoming mail server & outgoing mail server, & create an
    server action to notificate when is created a new project issue.

    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
        "fetchmail",
        "project_issue",
        ],
    "demo" : [
        "demo/project_issue_conf_demo.xml",
        ],
    "data" : [
        "data/mail_server_data.xml",
        "data/email_template_data.xml",
        "data/issue_conf_data.xml",
        "view/project_issue_send_mail_view.xml",
        ],
    "test": [],
    "installable" : True,
    "active" : False,
}
