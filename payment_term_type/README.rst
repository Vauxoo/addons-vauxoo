.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Payment Terms Type
==================

This module allow to show in payment terms the payment type depending of the
lines to compute
In Settings> Account you can find a selection field payment_type that can be
configurated with Based on quantity of payments or Based on date of payments.

Depending of the selection will affect the payment type:

* Credit
  The payment term will be credit type when the payments are covered in just
  two ore more exhibitions (partialities) or \n when the payments are covered
  in just one or more exhibitions, but the payments will be done in a different
  day that the sale order confirmation day

* Cash
  The payment term will be cash type when the payments have been covered in
  just one exhibition. without matter the date of payment or when the payments
  have been covered in just one exhibition, in the same day that the  sale
  order be confirmed.


Installation
============

To install this module, you need to:

#. Do this ...

Configuration
=============

To configure this module, you need to select between Based on quantity of
payments or Based on date of payments in accounting settings

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Vauxoo/addons-vauxoo/issues/new?body=module:%20payment_term_type%0Aversion:%201.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**&title=[8.0]%20yoytec_rma_workflow:%20problem%20summary%20here>`_.

Credits
=======

Contributors
------------

* Hugo Adan <hugo@vauxoo.com>

Maintainer
----------

This module is maintained by Vauxoo.

.. image:: https://www.vauxoo.com/logo.png
    :alt: Vauxoo
    :target: https://www.vauxoo.com
