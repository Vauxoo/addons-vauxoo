Purchase Requisition Currency
=============================

Adds the currency field in the purchase requisition model. When you use the
Request a Quotation button the purchase requisition currency new field will be
take into account to generate the purchase orders with a pricelist that have
the same currency. If there is not pricelist with the same purchase requisition
currency then it will raise an exception. You need to active some User
Technical Settings to take advantage of this functionality:

- Multi Currencies.
- Purchase Pricelist.
