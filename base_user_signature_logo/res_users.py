# coding: utf-8
from openerp.osv import osv, fields


class ResUsers(osv.Model):
    _inherit = 'res.users'
    _columns = {
        'signature_logo': fields.binary('Signature Logo')
    }
