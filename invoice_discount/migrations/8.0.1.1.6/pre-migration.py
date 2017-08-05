# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE account_invoice_line "
               "ADD COLUMN discount_amount NUMERIC;")
    cr.execute("UPDATE account_invoice_line "
               "SET discount_amount = discount * subtotal_wo_discount / 100")

    cr.execute("ALTER TABLE account_invoice "
               "ADD COLUMN discount_amount NUMERIC;")
    cr.execute("UPDATE account_invoice inv "
               "SET discount_amount = view.da FROM( "
               "SELECT SUM(discount_amount) AS da, invoice_id FROM "
               "account_invoice_line GROUP BY invoice_id) AS view "
               "WHERE view.invoice_id = inv.id;")
