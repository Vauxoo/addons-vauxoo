# -*- coding: utf-8 -*-

from openerp.osv import fields
from openerp.osv import osv


class project_image(osv.Model):
	
	_inherit = "project.project"
	_columns = {
		'logo': fields.related('partner_id', 'image', string="Logo", type="binary"),
	}
