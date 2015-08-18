Product Properties by Category
==============================

This module add a new section called "Product Property" in the Product Category
form view to manage a group of common default values to be set at the Products
that belongs to the Category.

When you change the Internal Category of the Product the default values defined in
the Category for the Products will be set. This configuration is set but is not mandatory,
you can manually change the Products fields as you need.

For the current version, only works with the "Call For Bids" Product field.
When you update your Products Internal Category the "Call For Bids" field
in the Product will be updated with the default value given to the field
"Call For Bids" defined in the Product Category. If the Product Category
have not defined a default value for "Call For Bids" then will look into the
parent Product Category an so on until find a default value. If not default
value is set on any of the parent product category then the "Call For Bids"
field in Product will be set to False.