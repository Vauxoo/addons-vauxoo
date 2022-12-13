.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Stock Manual Transfer:
----------------------

This module allows you to trigger transfers using a specific route, as it were triggered by a reordering rule.

- In order to be able to make the transfer, the user must belong to the stock manual transfer group:

.. image:: ./static/description/manual_transfer_group.png
    :alt: Manual transfer group
    :width: 600px

- And the route must be allowed to make manual transfers:

.. image:: ./static/description/manual_transfer_route.png
    :alt: Manual transfer field on the route
    :width: 600px

A new item in the operations menu of the stock module will be shown in order to create Manual transfers:

.. image:: ./static/description/manual_transfer_menu.png
    :alt: Manual transfer menu option
    :width: 600px

Once the Manual Transfer has been created as 'draft', a button in the form will validate the transfer
and create a Transfer (picking):

.. image:: ./static/description/manual_transfer_form.png
    :alt: Manual transfer form view
    :width: 600px

.. image:: ./static/description/stock_move_created.png
    :alt: Stock move created
    :width: 600px

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is Odoo.

To contribute to this module, please visit http://www.vauxoo.com
