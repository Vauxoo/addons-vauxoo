# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
    "name": "Add many followers in many task or project", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Task and Project", 
    "description": """

    This module is a help to add followers massive,
    mainly in project and task models

    Add an action windows in project and task model, to select any of these
    and set their followers

    Menu Name: Add Followers (act windows)

    How to Use:

        First you user need a groups, this groups is Add Followers/Managers

        Select the tree view all the documents to which you want to enter
        other followers

        Select at the actions of the option window "Add followers"

        The message already includes all projects which will be added as a
        follower

        It has the option of adding followers by "mail.group", "res.partner"
        or both playing with chebox to select which you want

        After all followers precionar selected the option to add followers and
        an email will be sent to each of them advising that they have been
        added to these documents (this may take a few seconds)

    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "AGPL-3", 
    "depends": [
        "project", 
        "user_story"
    ], 
    "demo": [], 
    "data": [
        "security/security_groups.xml", 
        "wizard/add_followers_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}