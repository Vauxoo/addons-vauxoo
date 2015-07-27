Account Invoice Per Journal Report
==================================

Adds a "Report" field on the journal model and a "Print Invoice" button on the
customer invoices view which calls a wizard to print an invoice on a report per
journal enviroment.

This module allows the generation of txt reports using the following
convention:

* Must be a report wizard type to return the txt report.
* The report wizard type must have the same name as his counterpart in pdf
  format concatenating the following string ' txt' in the report name.

In this way the module generates both reports, making available for download
the report txt.
