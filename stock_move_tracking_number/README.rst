.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Stock Move Tracking Number
==========================

This module will let you to manage a ``Tracking Number`` in the move record,
this way will be easy for you to organize the stock inventory.

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

**Tracking Number**

Add new field ``Tracking Number`` to the stock move model and visible form the
stock moves views and picking views with move lines listed. This new field can
be set manually for every move or can use a wizard to update the tracking
number to a group of moves. The tracking number field can only be updated if
the move is not in state ``done``.

**Batch Modify Tracking Numbers**

Add a button to the picking form view named ``Modify Tracking Numbers`` that
give the user the opportunity to modify tracking numbers in batch mode for all
or a subgroups of the current picking moves.

.. image:: picking_form_modify_button.png
   :alt: Button Modify Tracking Numbers at Picking Form View

After click the button ``Modify Tracking Numbers`` the wizard will open and
you should enter the new Tracking Number and select the move lines were this
new tracking number will be applied. If you want to exclude one of the line
you just need to click on the garbage icon over that move line. This will not
delete the move line, will only indicate that the new tracking number will not
be applied to that line.

.. image:: modify_tracking_number_wiz.png
   :alt: Modify Tracking Number Wizard

**Modifed Views**

Below are screenshots of the modified stock move and stock picking views:

- Move Tree view visible from the ``Warehouse > Traceability > Stock Move``
  menu. The ``Tracking number`` column is shown and you can make a search by
  Tracking Number directly or also you can Group by Tracking Number.

  .. image:: stock_move_tree.png
     :alt: Move Tree view

- Move Form view visible from the ``Warehouse > Traceability > Stock Move``
  after select one of the moves from the list view. A new section named
  ``Shipment Info`` was added.

  .. image:: stock_move_form.png
     :alt: Move Form view

- Move Lines in Picking Form view also show the tracking number for every move
  in the picking. You can edit the picking and change every move tracking
  number from this view.

  .. image:: picking_form_view.png
     :alt: Move Lines show Tracking Number in Picking Form View

- If you click over the move line in the picking form view you can open the
  move form. In this view also you can view the tracking number in the same
  format it was added to the stock move regular form view.

  .. image:: stock_move_form_from_picking.png
     :alt: Move Form View open from Picking Form View

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
stock_move_tracking_number%0Aversion:%20
8.0.1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

TODO
====

- add translations template and terms 

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
