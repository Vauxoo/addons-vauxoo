Purchase Changeless Move Lines
==============================

This module add a new functionality to retrict to add or modificate the move
lines belongs to a stock picking who was generate from a purchase order, in
order to not let the user to put the order out of position.

Set Picking restrictions from the Purchase Order
------------------------------------------------

A new boolan field ``Change Picking`` in the purchase order form view
determinate if the move lines in the generated stock picking can be modifcate
or not. By default the move lines can not be modificate unless it is explicit
indicate it in the purchase order.

The ``Purchases / Manager`` users are the only ones who can view and
modificate the ``Change Picking`` field.
