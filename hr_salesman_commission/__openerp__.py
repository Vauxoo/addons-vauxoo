
{
  'name' : "Sales Commissions Report",
  'version' : '1.0',
  'description' : """Sales Commissions Report
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
  'update_xml' : ['salesman_commission_view.xml',],
  'init_xml' : [],
  'demo_xml' : [],
  'depends' : ['account','account_voucher',"decimal_precision"],
  'installable' : True,
  'active' : False,
  'category' : 'Generic Modules/Human Resources',
  'author' : 'Vauxoo',
  'website' : 'http://openerp.com.ve',
}
