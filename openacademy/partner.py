# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields


class res_partner(osv.osv):

    """
    res_partner
    """
    _inherit = 'res.partner'
    _columns = {
        'is_instructor': fields.boolean('Is Instructor', required=False),
        'session_ids': fields.many2many('openacademy.session',
                                        'openacademy_attendee',
                                        'partner_id', 'session_id', 'Sessions'),
    }
res_partner()
