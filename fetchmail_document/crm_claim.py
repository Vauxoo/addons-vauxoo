# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
from tools.translate import _


class crm_claim(osv.osv):
    """
    crm_claim
    """
    _inherit = 'crm.claim'
    _log_create = True
crm_claim()
