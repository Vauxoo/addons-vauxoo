# coding: utf-8

from openerp.osv import osv, fields


class HrEmployee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'twitter': fields.char('Twitter', help="Paste here Twitter URL"),
        'github': fields.char('Github', help="Paste here Github URL"),
    }
    _defaults = {
        'website_published': False
    }
