Account Budget Improvements
===========================

- Added concept of "Estimated Forecast", It is an amount which represent the
  estimated amount per budget line that the person who report the budget line
  estimate comply in some moment.

- Added concept of "Actual Amount": The actual amount is the amount related to
  the sum of account in the fiscal position, with or without
  account_analityc_line this amount will be recorded in db and will change only
  with the change on the workflow.

- Added the concept of "Printed Budget" using the original workflow available
  on the budget we must include the concept of:

    - Posted Date: When the accountant Manager dictaminate that the amount is
      ready to be reviewed for the Local CFO.

    - Approved Date: When the local CFO says that the Budget can be sent to the
      CEO.

    - Received Date: When the CEO says that the budget is received.

The Account Budget view will be used to comply with need to show the executed
Budget per period.
