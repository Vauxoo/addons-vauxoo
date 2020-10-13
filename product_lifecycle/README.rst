.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Product Lifecycle
=================

This module applies a part of the product lifecycle management concept by
adding a status field and replacement product fields that will be used as
alternatives in sales operations when a product is discontinued.

Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular odoo
  module:

  - Download this module from `Vauxoo/addons-vauxoo
    <https://github.com/vauxoo/addons-vauxoo>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.

Configuration
=============

To configure this module, you need to:

* There is not special configuration for this module.

Usage
=====

**Lifecycle Status**

The status of the ``Product Variant`` is managed in the header of the product
form view as a clickable status bar widget, and with the default value ``Normal``.

The possible lifecycle states are:

- ``Normal``: An active product that can be sold or purchased.
- ``End of Lifecycle``: This means that the product is a discontinued product but there is still in stock.
- ``Obsolete``: This means that the product is a discontinued product and has no stock.

Search filters were added to search and group-by products by its lifecycle status.


**Replacement Products**

A new field section named ``Replacement Info`` was added to the ``Product Variant``
form view to hold the information about replacements products. This applies when
the product is a ``obsolete`` product. There are new fields:

- ``Replaced By``: Apply when the current product is an obsolete product,
  this field is the new product that will be replaced by the current product.
- ``Replace To``: This field holds an obsolete product and indicates that
  the current product is the new replacement of the obsolete product.

**Sale Order and Obsolete Products**

This module adds a widget to inform the product lifecycle status and avoid
selling an obsolete product.

Also, when you sell a ``End of Life`` product and there is no existence of
the product (stock inventory 0.0) the product state will be affected.
The product will change automatically from ``End of Life`` to ``Obsolete`` state.
This is an automatic action and it can be configured to be run in the system.


Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/addons-vauxoo/issues/new?body=module:%20
product_lifecyle%0Aversion:%20
12.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Katherine Zaoral <kathy@vauxoo.com> (Planer/Developer)
* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Auditor)
* Gabriela Mogollón <gmogollon@vauxoo.com>

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
