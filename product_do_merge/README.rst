Merge Duplicate Products
========================

Merge Products

We can merge duplicates products and set the new id in all documents of
product merged.

We can merge products using like mach parameter these fields:

* Name
* Reference

We can select which product will be the main product.

This feature do not change anything if the products to be merged have
operations in different units of measure.

It is possible to exclude some UoM fields in certain models from the above
check. For example, the field Weight UoM introduced by module 'Delivery'
will be often set in a UoM dimension different than that of the product.

In order to exclude a specific field, please go to 'Settings / Technical /
Database structure / Exclude UoM from Product Merge', then add the field
related to the product UoM that you want to exclude from the merge criteria.

This feature is in the follow path Warehouse/Tools/Duplicate products
also is created an action menu in the product view.
