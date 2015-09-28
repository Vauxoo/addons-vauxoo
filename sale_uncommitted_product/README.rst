Sale of Uncommitted Products
============================

* Adds a new state to the sale order model, committed
* Adds a new activity to the sale order workflow, commit
* Adds two new transitions from draft to commit,

  - One which could force commitment of sale order,
  - The other will check if any product does not overflow the availability

* Modifies the existing Transition from draft to router and changes it from commit to router.

* Adds a wizard so that it is possible to assign groups to the newly transitions.
* Adds two fields to the product.product model:

  - qty_committed: amounts the quantity of products in sale orders with state committed
  - qty_uncommitted: amounts the quantity of available to commit this amount is, qty_available + outgoing - qty_committed