.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Purchase Third Validation
=========================

This module added a third level to validator in purchase order, when the total
exceeds the amount configured only the users in the group
"Purchase third validation" will be able validate.

You can change the amount of third level in Settings/Purchase.

.. image:: purchase_third_validation/static/src/img/settings.png
    :width: 300pt

The workflow was changed in the process to validate a PO:

.. image:: purchase_third_validation/static/src/img/POwkf.png
    :width: 300pt

Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download repo in order to install purchase_third_validation module.

Contributors
------------

* Luis Torres <luis_t@vauxoo.com>

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
