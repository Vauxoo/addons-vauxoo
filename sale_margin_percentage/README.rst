.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Sale Order Gross Margin Percentage
==================================

This module change the margin calculation. Now, the sale order gross margin
percentage is calculated by the sum all the margin lines between the inverse
sum of all subtotals.

features:
---------
- Field to configure Margin Threshold on sale settings.
- Colors in sale order lines to point the margin threshold.
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
* Nhomar Hernandez <nhomar@vauxoo.com>
* Jose Suniaga <josemiguel@vauxoo.com>
