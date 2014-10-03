{
    "name": "Sales Commissions Report", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Generic Modules/Human Resources", 
    "description": """Sales Commissions Report
  Show the commissions based on the payments made by a particular salesman throughout the span of a specific period
  TODO:
  - Allow preparing the commisions to be paid (or been paid) to a particular salesman during certain period:
        * Ordered by Payments Number,
            + Show a Tree View
            + Allow to print a report
        * Grouped by Salesman,
            + Show a Tree View
            + Allow to print a report
  - Allow pay those commissions and make the regarding entries to the intended journal
  """, 
    "website": "http://openerp.com.ve", 
    "license": "", 
    "depends": [
        "account", 
        "account_voucher", 
        "decimal_precision"
    ], 
    "demo": [], 
    "data": [
        "salesman_commission_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: