.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

MRP Partial Prodution
=====================

In some case is needed start a production with partial reservation because you
can deliver your order in different parts. This module allow process a
manufacturing order with partial reservation, producing multiple times until
the order is completed.

The module add a new compute field to show the quantity available to produce
considering the number of the reservation in the products to consume. This
field is considered in all process and you cannot produce more than this field
indicates.

This module don't allow the creation of negative quant, this mean you cannot
force the production.


Contributors
------------

* Jose Morales <jose@vauxoo.com>

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
sytems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.
