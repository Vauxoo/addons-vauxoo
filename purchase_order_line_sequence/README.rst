Purchase Order Line Sequence
============================

New functionality to visually identificate the purchase order lines and sort
then asc.

A new field "sequence" was added to the lines of the purchase order for
automatic enumerate lines when they are created from the purchase order. The
sequence field exploits the special field functionality allowing drag and drop
the line to re-enumerate.

Features
--------

This sequence is a incremental number. It
increments one by one. You can also change the generate sequence number by
hand to set the sequence number you want. After you save the purchase order
lines will be re-ordered with the sequence value given.

Also the sequence field is validate to be unique per purchase order so the
sequence number to identificate lines can not be repeat into the lines of a
purchase order.
