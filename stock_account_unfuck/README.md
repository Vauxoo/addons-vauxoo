# Stock Account Unfuck
Currently, Odoo considers that all inventory leaves for products with Costing
Method equal to `average` must be booked at current Price Cost.

Chances that the Costing Price (average) changes are when products are incoming
from Suppliers.

According to Official Documentation the reason this is done is explained [here](https://www.odoo.com/documentation/user/9.0/accounting/others/inventory/avg_price_valuation.html#purchase-return-use-cas://www.odoo.com/documentation/user/9.0/accounting/others/inventory/avg_price_valuation.html#purchase-return-use-case)

## Odoo's Approach on Purchase Returns - Case Remaining Qty equals zero

|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 | 32.00     | 32.00   | 10       | 10       | 320.00    | 320.00    |
| 12/17/2016 | Purchase 02 | 48.00     | 40.00   | 10       | 20       | 480.00    | 800.00    |
| 12/19/2016 | Sale 01     | 40.00     | 40.00   | -16      | 4        | -640.00   | 160.00    |
| 12/21/2016 | Sale 02     | 40.00     | 40.00   | -2       | 2        | -80.00    |  80.00    |
| **12/23/2016** | **Pur. 01 Ret** | **40.00**     | **40.00**   | **-2**       | **0**        | **-80.00**    |   **0.00**    |

Looking at that rationale it is a feasible and acceptable solution that proves
a point.

If this is not done this way and returns are done at cost price of transaction we could end up
with either of two cases:

### Overvalued Inventory with no merchandise
|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 | 32.00     | 32.00   | 10       | 10       | 320.00    | 320.00    |
| 12/17/2016 | Purchase 02 | 48.00     | 40.00   | 10       | 20       | 480.00    | 800.00    |
| 12/19/2016 | Sale 01     | 40.00     | 40.00   | -16      | 4        | -640.00   | 160.00    |
| 12/21/2016 | Sale 02     | 40.00     | 40.00   | -2       | 2        | -80.00    |  80.00    |
| **12/23/2016** | **Pur. 01 Ret** | **32.00**     | **-**       | **-2**       | **0**        | **-64.00**    |  **16.00**    |

> It is to be noticed that under normal circumstances `Purchase 01 Return` can
> only be performed if the merchandise sold to the customer is first returned
> and then the supplier return can be fulfill as usual. Odoo will complain
> because there is no Quant available to be returned.

### Undervalued Inventory with no merchandise
|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 | 32.00     | 32.00   | 10       | 10       | 320.00    | 320.00    |
| 12/17/2016 | Purchase 02 | 48.00     | 40.00   | 10       | 20       | 480.00    | 800.00    |
| 12/19/2016 | Sale 01     | 40.00     | 40.00   | -16      | 4        | -640.00   | 160.00    |
| 12/21/2016 | Sale 02     | 40.00     | 40.00   | -2       | 2        | -80.00    |  80.00    |
| **12/23/2016** | **Pur. 02 Ret** | **48.00**     | **-**       | **-2**       | **0**        | **-96.00**    | **-16.00**    |

## New Approach on Purchase Returns - Case Remaining Qty greater than zero
However, for the following case the inventory that leaves cannot be booked at
average cost because that implies an increase/decrease of inventory valuation
without support as shown below.

|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 |  32.00    |  32.00  |  10      | 10       |  320.00   |  320.00   |
| 12/17/2016 | Purchase 02 |  48.00    |  40.00  |  10      | 20       |  480.00   |  800.00   |
| 12/19/2016 | Sale 01     |  40.00    |  40.00  | -16      | 4        | -640.00   |  160.00   |
| 12/21/2016 | Purchase 03 | 400.00    | 256.00  |   6      | 10       | 2400.00   | 2560.00   |
| **12/22/2016** | **Pur. 03 Ret** | **256.00**    | **256.00**  |  **-6**      | **4**        |**-1536.00**   | **1024.00**   |
| 12/23/2016 | Sale 02     | 256.00    | 256.00  |  -2      | 2        | -512.00   |  512.00   |

> This is a real case scenario. Purchase Analyst wrongly set currency on
> `Purchase 03` which increases the cost of merchandise in local currency,
> without being noticed it goes freely to Goods Receipt and Warehouse Analyst
> receives the merchandise. Average is hugely increased and that action goes
> unnoticed. Accounting People realizes about the mistake - wrong currency -
> and triggers the process for merchandise returns. Meanwhile, Salesmen prepare
> and successfully sales merchandise to one of his customers. Accounting
> Analyst realizes that CoGS on `Sale 02` was wrongly booked and Inventory
> Valuation is overvalued and ultimately average is wrongly computed.

Because the process previously exposed, it is proposed that Purchase Returns to
be performed at Cost of Transaction when remaining inventory is greater than
zero which will result in a Stock Card like the following:

|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 |  32.00    |  32.00  |  10      | 10       |  320.00   |  320.00   |
| 12/17/2016 | Purchase 02 |  48.00    |  40.00  |  10      | 20       |  480.00   |  800.00   |
| 12/19/2016 | Sale 01     |  40.00    |  40.00  | -16      | 4        | -640.00   |  160.00   |
| 12/21/2016 | Purchase 03 | 400.00    | 256.00  |   6      | 10       | 2400.00   | 2560.00   |
| **12/22/2016** | **Pur. 03 Ret** | **400.00**    |  **40.00**  |  **-6**      | **4**        |**-2400.00**   |  **160.00**   |
| 12/23/2016 | Sale 02     |  40.00    |  40.00  |  -2      | 2        |  -80.00   |   80.00   |


## New Approach on Sales Returns

Besides, incoming merchandise not coming from suppliers does not alter the
average cost price, i.e., sales returns.

For example, if merchandise is sold to a customer and after some time and some
purchase transactions, merchandise from the previous Sales Order is returned.
According to Odoo Sales are return at current average price and not at Sales
average price. In doing so, means that inventories will end building up
creating profits or losses because the original value was less or greater.

|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 |  32.00    |  32.00  |  10      | 10       |  320.00   |  320.00   |
| 12/17/2016 | Sale 01     |  32.00    |  32.00  |  -6      | 4        | -192.00   |  128.00   |
| 12/19/2016 | Purchase 02 |  48.00    |  40.00  |   4      | 8        |  192.00   |  320.00   |
| **12/22/2016** | **Sale 01 Ret** |  **40.00**    |  **40.00**  |   **6**      | **14**       |  **240.00**   |  **560.00**   |

As we can see Sale 01 Delivery was booked as follows:
| Account           |  Debit | Credit |
| :---------------- | -----: | -----: |
|Stock Out          |  192.00|        |
|Inventory Valuation|        |  192.00|

Sale 01 Invoice was booked as followed:
| Account           |  Debit | Credit |
| :---------------- | -----: | -----: |
|Receivable         |  250.00|        |
|Income             |        |  250.00|
|CoGS               |  192.00|        |
|Stock Out          |        |  192.00|

Returns - Delivery & Invoice - were booked as follows:
| Account           |  Debit | Credit |
| :---------------- | -----: | -----: |
|Inventory Valuation|  240.00|        |
|Stock Out          |        |  240.00|

Sale 01 Invoice was booked as followed:
| Account           |  Debit | Credit |
| :---------------- | -----: | -----: |
|Income             |  250.00|        |
|Receivable         |        |  250.00|
|Stock Out          |  240.00|        |
|CoGS               |        |  240.00|

As we can see, there is a net increase on Inventory Valuation and the CoGS is
greater than that expected to be refunded by the Return

What is expected is a Stock Card like this:

|    Date    | Transaction | Unit Cost | Average | Move Qty | Inv. Qty | Move Val. | Inv. Val. |
| :--------: | :---------: | --------: | ------: | -------: | -------: | --------: | --------: |
| 12/15/2016 | Purchase 01 |  32.00    |  32.00  |  10      | 10       |  320.00   |  320.00   |
| 12/17/2016 | Sale 01     |  32.00    |  32.00  |  -6      | 4        | -192.00   |  128.00   |
| 12/19/2016 | Purchase 02 |  48.00    |  40.00  |   4      | 8        |  192.00   |  320.00   |
| **12/22/2016** | **Sale 01 Ret** |  **32.00**    |  **_36.57_**  |   **6**      | **14**       |  **192.00**   |  **512.00**   |

Which results on a change on average cost when merchandise is returned and
keeps both the Inventory Valuation and CoGS in harmony

# Conclusions:
    - When returns are made to suppliers and remaining quantity is zero Odoo's
      approach will be used leading to avoid over/under-valuation of inventory,
      i.e., average cost price will be used.
    - When returns are made to suppliers and remaining quantity is different
      than zero then the transaction cost at which the merchaside was let in
      will be used.
    - When returns are made to stock from other locations these are done a
      transaction cost.
