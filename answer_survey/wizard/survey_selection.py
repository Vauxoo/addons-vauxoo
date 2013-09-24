# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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

from lxml import etree

from openerp.osv import fields, osv
from openerp.tools.translate import _

class survey_name_wiz(osv.TransientModel):
    _inherit = 'survey.name.wiz'

    def action_next(self, cr, uid, ids, context=None):
        res = super(survey_name_wiz, self).action_next(cr, uid, ids, context)
        
        res.update( {
            'target': 'inline',
        })
        return res

class survey_question_wiz(osv.TransientModel):
    _inherit = 'survey.question.wiz'

    def action_next(self, cr, uid, ids, context=None):
        res = super(survey_question_wiz, self).action_next(cr, uid, ids, context)
        
        res.update( {
            'target': 'inline',
        })
        return res

