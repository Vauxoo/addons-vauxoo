Purchase Requisition Line Description
=====================================

A description is added in purchase requisition lines

Add description on product.

Technical warning

Add method override to def make_purchase_order from purchase_requisition

When you install this module in the server show this warning:

WARNING: unable to set column name of table purchase_requisition_line not null !

When you upgrade this module the field 'name' is set product name and
this warning not be displayed more.