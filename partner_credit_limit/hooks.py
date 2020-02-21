# Copyright 2020 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, SUPERUSER_ID
from odoo.tools import column_exists


def post_init_hook(cr, registry):
    _set_credit_limit(cr, registry)


def _set_credit_limit(cr, registry):
    """Set the credit limit field to partners

    Since this module enables company-specific credit limits, their values need
    to be set manually for each company.
    """
    if not column_exists(cr, 'res_partner', 'credit_limit'):
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
        SELECT id, credit_limit
        FROM res_partner
        WHERE credit_limit != 0;
    """)
    # Create a dict {partner_id: credit limit, ...}
    credit_limit_values = dict(env.cr.fetchall())

    # Set values for each company, creating corresponding properties
    companies = env['res.company'].search([])
    property_model = env['ir.property']
    for company in companies:
        property_model.with_context(force_company=company.id).set_multi(
            model='res.partner',
            name='credit_limit',
            values=credit_limit_values)

    # Drop column that contains old values
    cr.execute("""
        ALTER TABLE res_partner
        DROP COLUMN IF EXISTS credit_limit;
    """)
