.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Product Price Cost in USD:
==========================

This module adds a field to handle cost in USD on products.
The approach is to have the USD as the base currency,
so that the sale prices in company currency can be
kept up to date through the exchange rate.

Features:
---------
- New 'Cost in USD' field on the Product form.
- Validate 'Cost in USD' so that it is not less than the list price of the
  supplier.
- Avoid save a 'Cost in USD' when product does not has assigned a supplier
  with price in USD.
- Allowed pricelist computation based on Cost in USD.
- Added unit tests to validate constrains and pricelists computation.
- Compatibility with the module `sale_margin
  <https://github.com/odoo/odoo/tree/10.0/addons/sale_margin>`_


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Jose Suniaga <josemiguel@vauxoo.com>
