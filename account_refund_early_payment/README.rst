.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Refund Early Payment
============================

This module adds the option Early Payment to create Customer Refund

You can create one Customer Refund with Early Payment for several invoices
from tree view

.. image:: /account_refund_early_payment/static/src/img/refundfrominvoices.png
    :width: 300pt

Choosing the option Refund Method Early Payment
You can set one percent or another amount to create customer refund. By
default is set with percent of 5.0

.. image:: /account_refund_early_payment/static/src/img/refundwizard.png
    :width: 300pt

The customer refund created shows in Source Document all invoices that
were used in this customer refund

.. image:: /account_refund_early_payment/static/src/img/refundsourcedocument.png
    :width: 300pt

The section Payment depicts all invoices that were reconciled with this
customer refund

.. image:: /account_refund_early_payment/static/src/img/refundpayment.png
    :width: 300pt

This module splits into journal entry of customer refund
creating one journal item per invoice in order to create independent reconciliations

.. image:: /account_refund_early_payment/static/src/img/refundjournalentries.png
    :width: 300pt

Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download repo in order to install account_refund_early_payment module.

Contributors
------------

* Humberto Arrocha <hbto@vauxoo.com>
* Yanina Aular <yani@vauxoo.com>
* Julio Serna <julio@vauxoo.com>

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
