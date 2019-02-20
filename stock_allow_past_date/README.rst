Stock Allow Past Date
=====================

This module add the functionality to let to validate a picking with a past
date and generate the move/quant with the past date instead the current date.
It is considered as an stock module's bugfix. This module by it self do not
change the way that picking is created, just add a workaround that can be
manage with a key in context to let to create the picking in a past date.

This module is not for final user use, is more like a tool to be use for
another modules (that take this module as dependency) to let then create
picking and quants in past date. This is mostly used when creating historical
data demo. And is not needed for regular creating picking purpose.

What do you need to create picking/quant in a past date:

#. Create the demo data of the picking and move. You need to set the ``date``
   field in both records. This field is the one re-used to set it in the
   quant.
#. You need to call the picking methods with a prefix context activating the
   "Allow Past Date" mode. For this just add the
   ``with_context({'allow_past_date_quants': True})``. This is required to be
   use in the call of the ``action_confirm()``, ``do_transfer()``,
   ``action_done()`` picking methods and whatever other method that influence
   in the quant creation and validation.

**NOTE**: In case that you will like to add more data demo, we strongly
recommend to use Vauxoo/csv2xml tool. Update stock_allow_past_date/test/csv
file and then run the csv2xml command to generate the proper xml ``csv2xml
update -m stock_allow_past_date -csv path/to/stock_allow_past_date/tests/csv -n
path/to/stock_allow_past_date/demo -co ''``

TODO
====

- Odoo picking Expected date (`date_expected`) set in help that this date is
  the one that is used when in the move. I check this an this is not happened,
  please review again and then report.
- Check via unit test that the quant in_date/write date is the same.
