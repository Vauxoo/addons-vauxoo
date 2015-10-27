.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Warehouse Interim Receipt
=========================

This module add an internal warehouse number of receipt to the stock move to
control the internal inventory.

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

**Warehouse Receipt Model**

Add a new module named ``Warehouse Receipt`` that holds the information about
warehouse interim receipt number. This number is related to the stock move.

- The ``Warehouse Receipt`` field can be edit in the stock move form view in
  the ``Shipment Info`` section.
  
  .. image:: stock_move_form.png
     :alt: Stock Move Form View

- The ``Warehouse Receipt`` field is also shown in the stock move list view.

  .. image:: stock_move_tree.png
     :alt: Stock Move Tree view

- You can filter the stock moves list searching or grouping by ``Warehouse Receipt``.
  
  .. image:: stock_move_search.png
     :alt: Stock Move New Filters

- The ``Picking`` form view that list the move lines also show the ``Warehouse
  Receipt`` per move.

  .. image:: stock_picking_moves.png
     :alt: Move lines in Picking Form View

- Add a wizard named ``Modify Warehouse Receipt Numbers`` visible from the
  picking form view that let to replace multiple warehouse receipt numbers for
  move lines of the same picking.

  .. image:: modify_warehouse_receipt_button.png
     :alt: button to access to the batch modigy wizard

  .. image:: modify_warehouse_receipt_form.png
     :alt: Modify Warehouse Receipt wizard

**Warehouse Receipt Input**

Add new wizard that print a report, given a list of purchase order will show
the user the move lines associated to that purchase order group by purchase
order and warehouse receipt number. You can access to the functionality by
going to ``Reporting > Warehouse > Warehouse Receipt Input`` menu.

.. image:: warehouse_receipt_wizard_menu.png

At the wizard you can introduce the Bill of Lading (BOL) Number this is
optional, required add one or more purchase order that you want to show in the
report. Then you need to add the report name and if you want or not to
save the query by generating a search filter that with hold the same query
name.

.. image:: warehouse_receipt_wizard.png

The result is a tree view showing the stock moves of the selected purchase
orders. This view group the moves by purchase order and then by warehouse
receipt number.

.. image:: warehouse_receipt_wizard_result.png

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
warehouse_interim_receipt%0Aversion:%20
8.0.1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

TODO
====

- This module add a ``purchase_order_id`` field to the ``stock.move``. This
  could be a generic functionality need to be consider to be add in a new
  generic module.

Credits
=======

**Constributors**

* Rafael Silva <rsilvam@vauxoo.com> (Planner/Auditor)
* Katherine Zaoral <kathy@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
