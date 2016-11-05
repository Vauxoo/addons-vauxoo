.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Shipping Date on Sale Order
============================

This module add a field into Sale Order that show the Date by which the
products are sure to be delivered.  In contrast to commitment date, not only is
taken into account the product lead time, but also the resupply delay, the
delivery lead time from supplier and the manufacturing delay.

Technically, the shipping date field comes to replace the commitment date.

Usage
=====
In order to obtain the best performance for computations of dates, you should:
- For purchase date computation, you should have configured the supplier information for each product that can be buy
- For manufacturing date computation, you should have configured the reordering rules for each product that can be manufactured.
- For resupply date computation, you should have configured the lead time in reordering rules and set delay on the procurement rule in the resupply routes.

Known issues / Roadmap
======================

* Not tested yet in a multi-company environment
* In all computed quantities, are used the whole product quantity on line. A
  good improvement is do computation with split quantities, as `MTS+MTO <https://github.com/OCA/stock-logistics-warehouse/tree/8.0/stock_mts_mto_rule>`_ module approach

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Vauxoo/addons-vauxoo/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/vauxoo/
addons-vauxoo/issues/new?body=module:%20
sale_order_shipping_date%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Technical Sketch
================

To build the compute shipping date method, is required the followings methods:

* **compute_warehouse_date**: Determine the most early date where a product is sure that could be delivered from a given warehouse. If the forecasted quantity is not enough to complete product qty requested, then is returned False.

    - return **false** there is not enough virtual availability in warehouse, comparing with product qty from order_line
    - if exist virtual avalability iterate date starting from order_date until date when availability is complete in warehouse, passing the date to product context.
    - Increase order line delay to resulted date

* **compute_resupply_date**: date when product will come to a given warehouse from others warehouses

    - return **false** there is not enough virtual availability without warehouse filter, comparing with product qty from order_line.
    - get resupply routes filtering by supplied warehouse
    - iterate routes, and check virtual availability in supplier warehouse
    - return **false** there is not enough virtual availability in supplier warehouse
    - call compute_warehouse_date function using supplier warehouse as parameter,
    - increase the route's procurement rule delay to resulted date

* **compute_purchase_date**: date when product will come to a given warehouse from a purchase order

    - create a dates list iterating supplierinfo, and sum each supllier delivery lead time to the order_date
    - return **false** there is not supplierinfo for this product.
    - if exist supplierinfo return the max date from dates list

* **compute_manufacturing_date**: date when product will come to a given warehouse from a production order

    - get bom, filtering by product template, iterate bom lines, create a dates list to get the product date expected using compute_warehouse_date function
    - return **false** there is not a BoM for this product.
    - if exist BoM return the max date from dates list
    - increase manufacturing lead time to max date expected


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
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.

