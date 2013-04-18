from openerp.osv import fields, osv
from openerp.tools.translate import _



class account_invoices(osv.Model):
    """
    account_invoices
    """

    _inherit = 'account.invoice'

    def print_invoice(self, cr, user, ids, context={}):
        """
        Description about method

        @param cr: cursor to database
        @param user: id of current user
        @param ids: list of record ids to be process
        @param context: context arguments, like lang, time zone

        @return: return a result
        """

        result = None
        # TODO : Business Process
        return {'type': 'ir.action.report.xml',
                'report_name': 'account.invoice'}

