Split Invoices
==============

This module allows to split a customer invoice, so the customer may pay a
percentage of the invoice amount and, optionally,  create a new invoice
to pay the remaining amount later.


Usage
=====

To use this module, you need to:

1. Go to any invoice in draft mode
2. Click on the menu Actions → "Split Invoice"
3. Fill the percent by which the invoice will be split, and check/uncheck if a
   new invoice will be created for the  remaining amount
4. Click on the "Split" button. When a new invoice is created, you'll be
   redirected to a list view where both invoices are displayed


Considerations
==============

When invoices are split, their lines are copied and product quantities are
divided which may produce non-integer quantities. This process is done without
taking into account unit of measures. That means, if a line contains, for
instance, three shirts, and the invoice is split to 50%; then the invoice will
be for 1.5 shirts after the invoice is split, even though that is not
possible in practice.


Credits
=======

**Contributors**

* Luis González <lgonzalez@vauxoo.com> (Developer)
* Yanina Aular <yanina.aular@vauxoo.com> (Planner/Auditor)


Maintainer
==========

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
