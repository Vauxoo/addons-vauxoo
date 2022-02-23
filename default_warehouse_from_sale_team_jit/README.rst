Default Warehouse from Sales Team + Just In Time Scheduling
===========================================================

This module is just to ensure the module "Default Warehouse from Sales Team"
works correctly when sold products are configured to be reserved immediately
after sales order confirmation, i.e. module "Just In Time Scheduling"
(``procurement_jit``) is installed.

This helps to avoid access errors when product reservation of sale orders
requires access to warehouses not allowed to current user on their sales teams.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/addons-vauxoo/issues/new?body=module:%20
default_warehouse_from_sale_team_jit
%0Aversion:%20
14.0
%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

Contributors
------------

- Luis González <lgonzalez@vauxoo.com>

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
