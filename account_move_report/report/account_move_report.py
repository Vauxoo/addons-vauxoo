from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.account_move_report.account_entries_report'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        total_debit_credit = self.get_total_debit_credit(docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'total_debit_credit': total_debit_credit,
        }

    def get_total_debit_credit(self, docs):
        res = {}
        for doc in docs:
            sum_tot_debit = sum(doc.line_ids.mapped('debit'))
            sum_tot_credit = sum(doc.line_ids.mapped('credit'))
            res.update({doc.id:
                        {'sum_tot_debit': sum_tot_debit,
                         'sum_tot_credit': sum_tot_credit}})
        return res
