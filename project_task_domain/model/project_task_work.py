# !/usr/bin/python
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

from openerp.osv import osv
from openerp.tools.translate import _
import time


class project_task_work(osv.Model):
    _inherit = 'project.task.work'

    def onchange_hours(self, cr, uid, ids, hours=None, context=None):
        if context is None:
            context = {}
        warning = {}
        if hours < 0:
            warning = {'title': _('Warning!'),
                       'message': _('Are you sure that you want to charge '
                                    'hours in negative?')}
        return {'warning': warning}

    def onchange_date(self, cr, uid, ids, date=None, context=None):
        if context is None:
            context = {}
        warning = {}
        if date > time.strftime('%Y-%m-%d %H:%M:%S'):
            warning = {'title': _('Warning!'),
                       'message': _('Are you sure that'
                                    ' you want to charge a future date?')}
        return {'warning': warning}
