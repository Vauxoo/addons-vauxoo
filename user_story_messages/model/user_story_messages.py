# -*- encoding: utf-8 -*- #
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).                           #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)                         #
#    Planified by: Nhomar Hernandez (nhomar@vauxoo.com)                    #
#    Finance by: Vauxoo <info@vauxoo.com>                                  #
#    Audited by: Moises Lopez <moylop260@vauxoo.com>                       #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################

from openerp.osv import fields, osv
from openerp.addons.base_status.base_stage import base_stage

class user_story(base_stage, osv.osv):
    _name = "project.user.story"
    _description = "User Story"
    _date_name = "date_start"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'user_story_messages.mt_user_story_started': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['new', 'draft'],
            'user_story_messages.mt_user_story_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open',
            'user_story_messages.mt_user_story_ready': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
        },
    }
