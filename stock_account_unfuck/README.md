# Stock Account Unfuck
Currently, Odoo considers that all inventory leaves for products with Costing
Method equal to `average` must be booked at current Price Cost.

Chances that the Costing Price (average) changes are when products are incoming
from Suppliers.

According to Official Documentation the reason this is done is explained [here](https://www.odoo.com/documentation/user/9.0/accounting/others/inventory/avg_price_valuation.html#purchase-return-use-cas://www.odoo.com/documentation/user/9.0/accounting/others/inventory/avg_price_valuation.html#purchase-return-use-case)

## Odoo's Approach on Purchase Returns

|        Date         | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :-----------------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/20/2016 04:53:50 | Purchase 01 | 32.00     | 32.00   | 10       | 10       | 320.00    | 320.00    |
| 12/20/2016 05:08:49 | Purchase 02 | 48.00     | 40.00   | 10       | 20       | 480.00    | 800.00    |
| 12/20/2016 05:10:14 | Sale 01     | 40.00     | 40.00   | -16      | 4        | -640.00   | 160.00    |
| 12/20/2016 05:10:56 | Sale 02     | 40.00     | 40.00   | -2       | 2        | -80.00    |  80.00    |
| **12/20/2016 05:12:19** | **Pur. 01 Ret** | **40.00**     | **40.00**   | **-2**       | **0**        | **-80.00**    |   **0.00**    |

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
