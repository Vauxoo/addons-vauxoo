supplier_invoice_number_unique
==============================

This module validates that the supplier_invoice_number field is not repeated

The validation doesn't consider uppercase and lowercase, if you have one invoice with supplier
invoice number:  "A123" and you try validate another invoice with the supplier
invoice number: "a123", the validation is going to show the message: "Error you can not validate
the invoice with supplier invoice number duplicated"