Currently, Odoo considers that all inventory leaves for products with Costing
Method equal to `average` must be booked at current Price Cost.

Chances that the Costing Price (average) changes are when products are incoming
from Suppliers.

According to Official Documentation the reason this is done is explained here (URL)

[[Here goes an example of Odoo's Purchase Returns]]

Looking at that rationale it is a feasible and acceptable solution that proves
a point.

However, for the following case the inventory that leaves cannot be recorded at
average cost because that implies an increase/decrease of inventory without
support as shown below.

[[Here goes an example of New Proposal of Purchase Returns]]


Then it is proposed that:

    - When returns are made to suppliers and remaining quantity is zero Odoo's
      approach will used loeading to avoid over/under-valuation of inventory,
      i.e., average cost price will be used.
    - When returns are made to suppliers and remaining quantity is different
      than zero then the transaction cost at which the merchaside was let in
      will be used.

Besides, incoming merchandise not coming from suppliers does not alter the
average cost price.

For example, if merchandise is sold to a customer and after some time and some
purchase transactions, merchandise from the previous Sales Order is returned.
According to Odoo Sales are return at current average price and not at Sales
average price. In doing so, means that inventories will end building up
creating profits or losses because the original value less or greater.

[[Here goes an example of stock_card for customer returns]]

[[Here some examples of Journal Entries are to be made]]

It proposed that returns are to be made a Average Price of transaction.
