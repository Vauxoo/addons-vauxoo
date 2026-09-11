from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import single_email_re


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("email", "active")
    def _check_email_internal_user(self):
        """If the partner belongs to an internal user, validate the email matches the user login"""
        # Records loaded from a module's data or demo files are not user input, so the safeguard has nothing to
        # protect there and enforcing it only blocks module installation. Odoo's own demo data is the proven case:
        # l10n_mx_hr_payroll and l10n_us_hr_payroll give internal users a login that differs from the partner
        # email on purpose, the failed demo load is rolled back inside a savepoint without a previous flush, and
        # the pending writes of the module's regular data are lost with it, breaking every module installed later.
        # install_mode is the flag Odoo sets while importing XML/CSV records and the one the core itself uses to
        # relax validations in that phase (res.currency, res.company, auth_signup).
        if self.env.context.get("install_mode"):
            return
        for partner in self:
            new_email = (partner.email or "").strip().lower()
            internal_users = partner.with_context(active_test=False).user_ids.filtered(lambda u: not u.share)
            internal_emails = {
                login.lower() for login in internal_users.mapped("login") if single_email_re.match(login)
            }
            if internal_emails - {new_email}:
                raise ValidationError(
                    self.env._(
                        "It's not possible to change this contact's email because it's associated to an internal user "
                        "and the new email doesn't match the user login.\n"
                        "- Contact's email: '%s'\n"
                        "- User login: '%s'",
                        new_email,
                        next(iter(internal_emails)),
                    )
                )
