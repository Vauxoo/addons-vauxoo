Account Voucher Tax
===================

The tax actually paid/cashed in the move of payment
===================================================

Creditable VAT.

 **NOTE:** This program is distributed in the hope that it will be useful,

It is the charge to all your payments i.e:
Bought a desktop that charge VAT on this desk is the creditable taxes

 **NOTE:** This program is distributed in the hope that it will be useful,

Retained VAT is retained by suppliers

- The rule is that only a natural person can hold a moral person.
- The exception to this rule is for freight and rental.

Caused VAT is that actually charged to customers.

- When you make a cash sale that VAT is caused
- When you make a sale on credit is transferred iva but when you pay that sale
  becomes caused VAT.

-----------------------------

Integration of payment taxes with account voucher
=================================================

Tested cases 1
--------------

* Payment one or more invoices of the same partner
* Payment in advance of one or more invoices of the same partner

Known failing Cases (to fix) 1
------------------------------

* Allow payment invoices with other movements like invoices, debit/credit refunds (resolved account_voucher_no_check_default module)
* When there are multiple payments may be that the amount of taxes paid is not equally payable by decimal rouding
* Error with Period field (not is set default)

-----------------------------

Integration of payment taxes with Bank Statement
================================================

Tested cases 2
--------------

* An statement bank with one imported invoice
* An statement bank with two or more imported invoices of the same partner
* An statement bank with two or more imported invoices of different partners
* Payment in advance of an invoice with partner(when the amount of the advance is less than or equal to the amount of the invoice)

Known failing Cases (to fix) 2
------------------------------

* Payment in advance that will pay more than one invoice
* When there are multiple payments may be that the amount of taxes paid is not equally payable by decimal rouding

 **Note:** The difference for loss or gain exchange rate or writeoff not generate journal items of payment taxes
 the fiscal experct adviced us it is right on that way.
