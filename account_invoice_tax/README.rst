Account Invoice Tax
===================

This module add tax relation to original tax, to be able to take off all data from invoices.

**Technical Warning:** This module add method override::

    def check_tax_lines from account_invoice
    def compute from account_invoice_tax
