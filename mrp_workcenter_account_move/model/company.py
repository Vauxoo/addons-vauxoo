# coding: utf-8

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    require_workcenter_analytic = fields.Boolean(
        string='Check Analytic on Workcenter',
        help=('When finishing production Cost Journal Entry Lines are '
              'created if this option is check Analytical accounts are '
              'required on Workcenters')
        )
