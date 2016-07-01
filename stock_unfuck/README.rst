.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Stock Unfuck
=====================

This module is created by the need to customize and improve the stock module
and its related modules.

Customized methods:

**quants_get_prefered_domain**: This method  for stock_quant object was changed to
specify the quants to use, send them by context avoiding choose another quant
not needed or create quant in specific locations(inventory, supplier,
production). 
The value sent in the context must be equal to that have to be
returned by this method; List of tuples with two elements inside each tuple,
where the first element is a recordset of stock quant, and the second one is
the quantity that must be used of the quant(first element)


You need to be sure that the quants sent by context can be used, considering
the main fields used in filters to find quants(qty, location_id, owner, lot_id,
package_id, reservation_id), because this change can be very useful or very
dangerous and it can create inconsistences in the inventory.


Because of we are sending this value by context we can send it from any method
even if this is not directly in stock_quant, for example the action_done method
for stock_move.

e.g.

move_brw.with_context({'unfuck_quants': [(stock.quant(59,), 1.0)]}).action_done()


Contributors
------------

* Jose Morales <jose@vauxoo.com>

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
