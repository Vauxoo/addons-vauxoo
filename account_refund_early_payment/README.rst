.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Refund Early Payment
============================

This module add the option Early Payment to create Customer Refund

You can create one Customer Refund by Early Payment from several invoices
from tree view

.. image:: account_refund_early_payment/static/src/img/refundfrominvoices.png
    :width: 300pt

Choosing the option Refund Method Early Payment
You can set one percent or amount to create customer refund
by default is set with percent of 5.0

.. image:: account_refund_early_payment/static/src/img/refundwizard.png
    :width: 300pt

The customer refund created show you in Source Document all invoices that
was used in this customer refund

.. image:: account_refund_early_payment/static/src/img/refundsourcedocument.png
    :width: 300pt

The section Payment show you all invoices that was reconciled with this
customer refund

.. image:: account_refund_early_payment/static/src/img/refundpayment.png
    :width: 300pt

This module make split into journal entry of customer refund
creating one journal item by invoice in order to create independent reconciliations

.. image:: account_refund_early_payment/static/src/img/refundjournalentries.png
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
