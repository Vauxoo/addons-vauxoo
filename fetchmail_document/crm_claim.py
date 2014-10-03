# -*- encoding: utf-8 -*-
from openerp.osv import osv


class crm_claim(osv.Model):

    """
    crm_claim
    """
    _inherit = 'crm.claim'
    _log_create = True
