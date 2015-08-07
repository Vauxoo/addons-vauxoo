MRP Consume Produce
===================

Add wizard to consume and produce.
It will be necesary to apply the patch patch/stock.patch located in
this module over the stock module::

    # use this command
    patch -b stock.py  stock.patch

Also is necesary to configure some permissions to use the implemented wizard.
You have to options: Go to check some options at the user:

- ``Access Rights > Other > Mrp Consume``
- ``Access Rights > Other > Mrp Consume / Manager``
- ``Access Rights > Other > MRP / Button Consume-Produce``

Or go to the ``Settings > Configuration > Manufacturing > Manufacturing Order``
and active the ``Real Consume and Produce`` option plus selecting a user type.
