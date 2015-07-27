Double validation in account_invoice
====================================

Invoice Double Validation

This module performs twice Account invoice validation,
performing the following.

* Add a group "group_validator"
* Hide the Validate button to the Draft invoice status
* Add a button "By Validate" visible to all.
* Add a state "By validating" to filter the invoices in the "By Validate"
  (Create the filter)
* Add the button "validate" so that only users with the group
  "group_validator" can press it.
* Users with the group "group_validator" will be able to validate
  the facura e.
* Consider that states and buttons need to be done by workflow.
