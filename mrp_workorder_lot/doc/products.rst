.. _products:

Products Management
===================

It agregate a 'product lines' model that contain information of the compatible
products for the workcenters, indicating the max capacity that product that
can be recive in the workcenter.

- Products Capacity:
- Products Quantity: at workcenter operation

WorkFlow
--------

1. Create a Manufacturing Order with its need fields.

   .. note:: the product associated to your Manufacturing Order need to have a
             routing associated

2. Confirm the recently created Manufacturing Order.
3. Change Manufacturing Order State to ``Production Started``
4. Active the Work Order Lots by clicking the ``Consumed`` button and fillin
   the wizard required fields.
5. Go to ``Manufacturing > Planning > Work Orders by Active Lot`` and start to
   consume an active Work Order Lot by clicking its Consume button (at the
   kaban card of the work order lot).
6. Now you need to process the the Work Orders in your Work Order Lot. For that
   you need to get every work order in your lot to a 'Finish' state. This will
   trigger a change to the Work Order Lot to ``Ready to Finish`` state.
7. At youre Manufacturing Order you need to click in the ``Products Produced``
   button and fill in the required fields and finalize clicking the ``Products
   Produced`` button. This will set the Work Order Lot form ``Ready to Finish``
   state to ``Done`` state indicating that the Work Order Lot have been
   Finished and will create the move of the Manufacturing Order final product
   that remains in the ``Manufacturing Order Form > Finished Products Page >``
   ``Produced Products section`` There you will see the complete information
   of the current produce product.
