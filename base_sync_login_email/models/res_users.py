from odoo import models
from odoo.tools import single_email_re


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        """If login and email matches and login is changed, change email accordingly"""
        new_login = vals.get("login")
        if (
            new_login
            and "email" not in vals
            and len(self) == 1
            and self.login.lower() == (self.email or "").lower()
            and self.login != new_login
            and single_email_re.match(new_login)
        ):
            vals["email"] = new_login
        return super().write(vals)
