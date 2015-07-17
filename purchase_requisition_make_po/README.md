Purchase Requisitions Description
=================================

This module allows you to manage your Purchase Requisition.

Add description on product.

Add analytic account on purchase requisition line, so the purchase order takes
the account analytic value from the purchase requisition.

Technical warning

Add method override to def make_purchase_order from purchase_requisition

When you install this module in the server show this warning:

WARNING: unable to set column name of table purchase_requisition_line not null !

When you upgrade this module the field 'name' is set product name and
this warning not be displayed more.