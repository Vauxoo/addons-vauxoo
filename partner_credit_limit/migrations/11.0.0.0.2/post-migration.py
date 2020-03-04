from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    set_credit_limit_values_to_partner(cr)


def set_credit_limit_values_to_partner(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute(
        """
        SELECT id, credit_limit, grace_payment_days FROM res_partner
        WHERE credit_limit != 0 OR grace_payment_days != 0""")
    data = env.cr.fetchall()
    for company in env['res.company'].search([]):
        for partner_id, credit_limit, grace_payment_days in data:
            env['res.partner'].browse(partner_id).with_context(
                force_company=company.id).write({
                    'credit_limit': credit_limit,
                    'grace_payment_days': grace_payment_days})
    env['ir.logging'].create({
        'name': 'partner_credit_limit migration',
        'level': 'info',
        'type': 'server',
        'dbname': env.cr.dbname,
        'message': data,
        'path': 'migration script',
        'line': 'migration script',
        'func': 'migration script'
    })
    env.cr.execute("""ALTER TABLE res_partner DROP COLUMN credit_limit""")
    env.cr.execute("""ALTER TABLE res_partner
                   DROP COLUMN grace_payment_days""")
