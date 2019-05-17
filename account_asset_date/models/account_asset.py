from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_is_zero


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    different_dates = fields.Boolean('Set Start Depreciation Date',
                                     default=False)


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    start_depreciation = fields.Date(
        'Start Depreciation Date', help=_(
            'Start Depreciation Date instead of Purchase Date'))
    different_dates = fields.Boolean('Set Start Depreciation Date',
                                     readonly=True,
                                     states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals.update({
            'start_depreciation': self._start_depreciation_date(
                vals['date'], vals['prorata']),
        })
        asset = super(AccountAssetAsset, self).create(vals)
        return asset

    def _start_depreciation_date(self, deprec_date, prorata=False):
        if prorata:
            return (datetime.strptime(deprec_date, DF) +
                    relativedelta(days=1)).strftime("%Y-%m-%d")
        if deprec_date[8:] == '01':
            return deprec_date
        elif deprec_date[5:7] == '12':
            return ('%d-01-01') % (int(deprec_date[:4]) + 1)
        return ('%s-%02d-01') % (deprec_date[:4], int(
            deprec_date[5:7]) + 1)

    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()
        if not self.different_dates:
            return super(AccountAssetAsset, self).compute_depreciation_board()

        posted_deprec_line_ids = self.env[
            'account.asset.depreciation.line'].search([
                ('move_check', '=', True), ('asset_id', '=', self.id)],
                order='depreciation_date')
        unposted_deprec_line_ids = self.env[
            'account.asset.depreciation.line'].search([
                ('move_check', '=', False), ('asset_id', '=', self.id)])

        # Remove old unposted depreciation lines. We cannot use unlink()
        # with One2many field
        commands = [(2, line_id.id, False) for line_id in
                    unposted_deprec_line_ids]

        if self.value_residual == 0.0:
            self.write({'depreciation_line_ids': commands})
            return True

        amount_to_depr = residual_amount = self.value_residual
        if (posted_deprec_line_ids and
                posted_deprec_line_ids[-1].depreciation_date):
            depreciation_date = (datetime.strptime(
                posted_deprec_line_ids[-1].depreciation_date,
                DF).date() + relativedelta(
                months=+self.method_period))
        else:
            depreciation_date = datetime.strptime(
                self._get_last_depreciation_date()[self.id], DF).date() if (
                    self.prorata) else (datetime.strptime(
                        self._start_depreciation_date(
                            self.start_depreciation[:4] + '-01-01' if (
                                self.method_period >= 12) else
                            self.start_depreciation), DF).date())

        day = depreciation_date.day
        month = depreciation_date.month
        year = depreciation_date.year
        total_days = (year % 4) and 365 or 366

        undone_dotation_number = self._compute_board_undone_dotation_nb(
            depreciation_date, total_days)

        for seq in range(len(posted_deprec_line_ids),
                         undone_dotation_number):
            sequence = seq + 1
            amount = self._compute_board_amount(
                sequence, residual_amount, amount_to_depr,
                undone_dotation_number, posted_deprec_line_ids,
                total_days, depreciation_date)
            amount = self.currency_id.round(amount)
            if float_is_zero(
                    amount, precision_rounding=self.currency_id.rounding):
                continue
            residual_amount -= amount
            vals = {
                'amount': amount,
                'asset_id': self.id,
                'sequence': sequence,
                'name': (self.code or '') + '/' + str(sequence),
                'remaining_value': residual_amount,
                'depreciated_value': self.value - (
                    self.salvage_value + residual_amount),
                'depreciation_date': depreciation_date.strftime(DF),
            }
            commands.append((0, False, vals))
            # Considering Depr. Period as months
            depreciation_date = date(year, month, day) + relativedelta(
                months=+self.method_period)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year

        self.write({'depreciation_line_ids': commands})

        return True

    @api.multi
    def _get_last_depreciation_date(self):
        if not self.different_dates:
            return super(AccountAssetAsset, self)._get_last_depreciation_date()

        self.env.cr.execute("""
            SELECT a.id as id,
              COALESCE(MAX(m.date),a.start_depreciation) AS date
            FROM account_asset_asset a
            LEFT JOIN account_asset_depreciation_line rel ON
                                                        (rel.asset_id = a.id)
            LEFT JOIN account_move m ON (rel.move_id = m.id)
            WHERE a.id IN %s
            GROUP BY a.id, m.date """, (tuple(self.ids),))
        result = dict(self.env.cr.fetchall())
        return result

    def onchange_category_id_values(self, category_id):
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            val = super(AccountAssetAsset, self).onchange_category_id_values(
                category_id)
            val['value'].update({
                'different_dates': category.different_dates,
            })
            return val

    def _compute_board_undone_dotation_nb(self, depreciation_date, total_days):
        res = super(AccountAssetAsset, self)._compute_board_undone_dotation_nb(
            depreciation_date, total_days)
        if not (self.prorata and self.different_dates):
            return res
        res = res - 1
        return res

    def _compute_board_amount(self, sequence, residual_amount,
                              amount_to_depr, undone_dotation_number,
                              posted_depreciation_line_ids, total_days,
                              depreciation_date):
        if not self.different_dates:
            return super(AccountAssetAsset, self)._compute_board_amount(
                sequence, residual_amount, amount_to_depr,
                undone_dotation_number, posted_depreciation_line_ids,
                total_days, depreciation_date)
        if sequence == undone_dotation_number:
            return residual_amount
        if self.method == 'linear':
            return amount_to_depr / (undone_dotation_number - len(
                posted_depreciation_line_ids))
        if self.method == 'degressive':
            return residual_amount * self.method_progress_factor
        return 0
