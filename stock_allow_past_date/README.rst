Stock Allow Past Date
=====================

This module add the functionality to let to validate a picking with a past
date and generate the move/quant with the past date instead the current date.

It is considered as an stock module's bugfix.

The field ``date`` need to be set in the picking and also in the move to
re-used and set it to the quant.

TODO
====

- Odoo picking Expected date (`date_expected`) set in help that this date is
  the one that is used when in the move. I check this an this is not happened,
  please review again and then report.
- Check via unit test that the quant in_date/write date is the same.
- Want to get better the way that overwrite the methods that write the
  move/quant date. Maybe using context instead.
