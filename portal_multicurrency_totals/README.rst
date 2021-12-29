Multi-Currency Totals in Portal
===============================

This module adds te feature to display total amounts by currency when accessing
documents through the portal:

- Quotations
- Sale orders
- Invoices

Usage
=====

To use this module, just go to the portal  and open a document list; you will see an extra footer with totals by currency.

When accessing quotations or sale orders, a total will be displayed per
currency:

    .. image:: portal_multicurrency_totals/static/description/totals_in_so.png
      :width: 400pt
      :alt: Totals in sale orders

When accessing invoices, paid and unpaid amounts will also be available:

    .. image:: portal_multicurrency_totals/static/description/totals_in_invoices.png
      :width: 400pt
      :alt: Totals in invoices

**Note**:
Even though records in state draft or cancelled may be displayed if they were
validated in some point, they're not considered when computing totals.

Credits
=======

Contributors
------------

* Luis González <lgonzalez@vauxoo.com>


Maintainer
==========

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is Odoo.

To contribute to this module, please visit https://www.vauxoo.com.
