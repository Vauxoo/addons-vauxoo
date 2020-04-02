from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    set_grace_payment_days_between_limits(cr)


def set_grace_payment_days_between_limits(cr):
    """In this migration the negative values of the grace_payment_day field are
      set to 0, as there is no point in negative of that value.
    Values greater than 999999 are also searched and set to 999999 to avoid
    OverflowError: date value out of range error.
    This to create the python constraint for this field.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.partner'].search([('grace_payment_days', '<', 0.0)]).write(
        {'grace_payment_days': 0.0})
    env['res.partner'].search([('grace_payment_days', '>', 999999)]).write(
        {'grace_payment_days': 999999})
