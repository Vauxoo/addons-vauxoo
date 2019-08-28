.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Product Sale Price in USD:
==========================

This module adds a field to handle sale price in USD on products.
The approach is to have another currency like base currency and the sale price in USD,
so that the sale prices in company currency can be calculate in base to the sale price in USD.

Features:
---------

- New 'Sale Price in USD' field on the product's form.
- The Sale Price of Odoo is calculated in base to Sale Price in USD daily with the last rate of dollar.
- Allow computation in pricelist based on Sale Price in USD.
- The sales price is calculated daily with the new rate
  The sales price is re-calculated if Sales Price in USD field is changed o setted.
- When the value of Sales Price USD is changed in the product, then, the Sale Price will be calculate too.
- The USD currency will be activated
- The Pricelist with formula will be activated

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Yanina Aular <yanina.aular@vauxoo.com>
