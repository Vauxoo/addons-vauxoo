.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Product Extension to track Segmentation Cost
============================================

In general this module includes cost segmentations for material(how much does
it cost in basic materials), landed (how much does it cost to assurance or
shipping it), production (how much cost to produce it in workcenters) and
subcontracting (how much does cost to let a third-party partner take charge to
produce or supply products or parts of it) needed to know where the cost for a
product goes. All segmentation included sums up not only the current product,
it includes also all segmented costs (BoMs in a BoM). And more detailed
functionalities that are contained in this module are the following:
* Recompute standard price from BoM of the product with a button on the
product based on the `segmentation` cost of the materials in the BoM
and the workcenters.
* Create accounting entries when needed by marking the check box
in Price update wizard for product.
* Recursive product price for BoM products is possible checking the
option available in Recompute price from BoM wizard for product. If not, the
cost will be updated using one-level BoM product calculation.
* Log every price and segmentation cost update in product messages only
to track price change for every product in your company.
* Set a bottom threshold for those price updates that make the product price
decrease, the default value is 0 (No decrease allowed).
* All update price wizards for products check if new cost meets the
bottom threshold limit.

Configuration
=============
In order to set the bottom threshold to every price update for your products
you must go to :
* Settings > Companies > Select your company and then open Configuration tab
and you will be able to see `Standard Price Bottom threshold (%)` field,
and set to a reasonable value you would consider.

Known issues / Roadmap
======================

* Top threshold limit is not currently supported.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Vauxoo/addons-vauxoo/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/vauxoo/
addons-vauxoo/issues/new?body=module:%20
product_extended_segmentation%0Aversion:%20
8.0.2.0.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Contributors
------------

* Humberto Arocha <hbto@vauxoo.com>
* Osval Reyes <osval@vauxoo.com>

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.

