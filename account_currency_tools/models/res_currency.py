from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.currency"

    @api.multi
    def _get_current_rate(self):
        self.ensure_one()
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id')\
            or self.env['res.users']._get_company().id
        # the subquery selects the last rate before 'date'
        # for the given currency/company
        query = """
            SELECT
                c.id,
                (SELECT
                    r.rate
                FROM
                    res_currency_rate AS r
                WHERE
                    r.currency_id = c.id
                AND
                    r.name <= %s
                AND
                    (r.company_id IS NULL
                    OR r.company_id = %s)
                ORDER BY
                    r.company_id, r.name DESC
                LIMIT 1) AS rate
            FROM
                res_currency AS c
            WHERE
                c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates.get(self.id) or 1.0
