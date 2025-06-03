from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import single_email_re


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("email", "active")
    def _check_email_internal_user(self):
        """If the partner belongs to an internal user, validate the email matches the user login"""
        for partner in self:
            new_email = (partner.email or "").strip().lower()
            internal_users = partner.with_context(active_test=False).user_ids.filtered(lambda u: not u.share)
            internal_emails = {
                login.lower() for login in internal_users.mapped("login") if single_email_re.match(login)
            }
            if internal_emails - {new_email}:
                raise ValidationError(
                    _(
                        "It's not possible to change this contact's email because it's associated to an internal user "
                        "and the new email doesn't match the user login.\n"
                        "- Contact's email: '%s'\n"
                        "- User login: '%s'",
                        new_email,
                        next(iter(internal_emails)),
                    )
                )
