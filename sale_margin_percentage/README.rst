.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Sale Order Gross Margin Percentage
==================================

This module changes the margin calculation. Now, the sale order gross margin
percentage is calculated by the sum of all the margin lines divided by the inverse
sum of all subtotals.

features:
---------

- Field to configure Margin Threshold on sale settings.
- Colors in sale order lines to indicate the margin threshold.
- Fix to 100 margin percentage when purchase price is not set.
- Fix to -100 margin percentage when price unit is not set.
- Fix to 0 margin percentage when product quatity is 0.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Katherine Zaoral <katherine.zaoral@vauxoo.com>
* Nhomar Hernández <nhomar@vauxoo.com>
* José Suniaga <josemiguel@vauxoo.com>

Maintainers
-----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
sytems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit https://www.vauxoo.com.
