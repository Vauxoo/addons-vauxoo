.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Update Purchase RFQ using XLS
=============================

The general purpose of this module is to update the
prices of products of a RFQ using a xls template.

When an RFQ is created and then this is sent by email,
this module attached to the mail an xls template
without prices so that the provider fill their prices.
Once send it to me back to the supplier module is able
to allow load the template and update the prices of
products taking into account the following 
considerations:

- If the product in the RFQ is equal in quantity and code to the request answered (filled excel) then only the cost is updated
- If the product in the RFQ is equal in code but not in quantity then updated quantity and price.
- If the product is listed in my RFQ but the supplier removed in their answered template, then this product will be removed of my RFQ.


Extras:
-------
- Attach to PO email a xls template.
- Adds a wizard for import /export xls templates in PO.


Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download repo in order to install controller_report_xls module.

Contributors
------------

* Jose Suniaga <josemiguel@vauxoo.com>

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
