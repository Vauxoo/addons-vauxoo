
.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

=======================
Sale Block Cancellation
=======================

Added a new button in Sale Orders to only allow cancel a SO when all the
pickings related with this are on ``ready to transfer`` or in
``waiting for another move`` state, or even with pickings on different states
if the moved product quantities are correctly returned.

The original button to cancell is added to a new group ``Force Sale Cancel``
to can allow cancel a Sale Order out of these cases.

Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular Odoo
  module:

  - Download this module from `Vauxoo/addons-vauxoo
    <https://github.com/vauxoo/addons-vauxoo>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/addons-vauxoo/issues/new?body=module:%20
sale_block_cancellation
%0Aversion:%20
8.0.0
%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Release Notes
=============

Credits
=======

**Contributors**

* Sabrina Romero <sabrina@vauxoo.com> (Planner/Auditor)
* Luis Torres <luis_t@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.

