MRP JIT extended
================

This module uses a wizard to merge an run the procurements of the selected
manufacturing orders (creating new manufacturing orders) to make a recursive
supply of the parent orders.

To apply patches needed use the command::

    patch -b "procurement/procurement.py" "prVocurement.py.patch"
    patch -b "mrp/mrp.py" "mrp.py.patch"
