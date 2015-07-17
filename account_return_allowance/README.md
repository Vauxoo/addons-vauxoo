Account Separate Return Allowance
=================================

OpenERP leaks of the feature necesary for some Latinamerican projects on
accounting, we need to make the discount explícit on the account move line
in the invoicing sale process because some taxes are exonerated with this
amount and is necesary to declare taxes.

Other accounting features is the credit notes, this are imputing amounts in
debit columns, this is a bad practices for an accounting point of view,
due to the generic information situation, what openERP Does actually is not
wrong but several custormers ask us correct this behaviour, and we decide
make it configurable.

After install this module, you must tell in company if you want use it or not.

Go to Administration > Companies and set the values to this feature on your
company.

Due to the generic issue, and in multilocalization enviroments, you will be
able to have this feature in one company or another it depends of your legal
context.

We add 2 fields on product category and product objects, this fields are the
accounts will be taken for this 2 features.

Allowance Account: Account taken to make account move lines when discounts
will be done.

With this module 2 move lines per product will be done on sale invoice::

                                Debit | Credit
    ===========================================|
    account receivable            D            |
    discount account on product            D   | [Account Configured on Product or Category.]
    ===========================================|

With this module 2 move lines per @Invoice@ when generic discount will be
applied on invoice [Planified but not done yet] will be done on sale
invoice::

                                Debit | Credit
    ===========================================|
    account receivable            D            |
    discount account on productS           D   | [Account Configured on Journal.]
    ===========================================|

For Accounting Especifications of return behaviour:

http://www.principlesofaccounting.com/chapter5/chapter5.html#return
