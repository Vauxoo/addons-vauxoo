POS Discount Invoice
====================

Normally odoo sets a negative line when a global discount is applied on a POS order and when that
order is invoiced, the negative line is kept in the Invoice. Depending the implementation or the
country, this behavior is not correct.

This module changes this behavior, to apply the discount proportionally in each invoice line.
