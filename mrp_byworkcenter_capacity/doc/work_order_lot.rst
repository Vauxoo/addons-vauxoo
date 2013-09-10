.. _work_order_lot:

Work Order Lot
==============

A Work Order Lot (**WOL**) is a new model that manage the work orders by a
set of this elements calling with the name of Lot.

This Lot is associated to the Manufacturing Order and its creation is
automatic by taking into account the workcenter products capaicty boottle
neck in a routing.

- A Work Order Lot is in progress (active) when is in 'open' or 'pending'
  state.
- When a Work Order Lot is in 'draft', 'picking', 'ready', 'done' or 'cancel'
  state can its associated work orders can change of state.

States
------

- **New** (``draft``): Te Lot have been created and is waiting to be activated.
- **Picking** (``picking``): The Lot its active and ready start the consume.
- **In Progress** (``open``): The Lot is already consumed and the work orders
  associated need to be started and finished.
- **Paused** (``pending``): Its set when some work order that belongs to the
  work order lot is in pending state, so also the work order lot its in
  Paused state.
- **Done** (``done``): The work order lot have produce a production lot.
- **Cancelled** (``cancel``):

Produce process
---------------

- *Case 1:* one2one relationship. One work order lot produce one production
  lot.
- *Case 2:* many2one relationship. More that one work order lot produce one
  production lot.
- *Case 3:* one2many relationship. One work order lot produce more the one
  production lots.

    .. figure:: images/wol_produce_spl.png
       :scale: 100 %
       :align: center
       :alt: Payroll Modules

       Módulos OpenERP para manejo de nómina

.. note:: This module only implements the case 1 of produce process with work
   order lots.

.. TODO: indicate the difference between work order lot and production Lot.
