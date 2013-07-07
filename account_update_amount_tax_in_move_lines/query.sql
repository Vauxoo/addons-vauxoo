-- IVA(16%) COMPRAS
UPDATE account_move_line
SET tax_id_secundary = (SELECT id FROM account_tax
			where name = 'IVA(16%) COMPRAS' and company_id in (SELECT id from res_company
									WHERE name = 'Agrinos México S.A. de C.V.'))
where id in (
SELECT id FROM account_move_line
where name in (SELECT name FROM account_tax
		where name = 'IVA(16%) COMPRAS' and company_id in (SELECT id from res_company
								WHERE name = 'Agrinos México S.A. de C.V.')))

--"IVA(11%) COMPRAS"
UPDATE account_move_line
SET tax_id_secundary = (SELECT id FROM account_tax
			where name = 'IVA(11%) COMPRAS' and company_id in (SELECT id from res_company
									WHERE name = 'Agrinos México S.A. de C.V.'))
where id in (
SELECT id FROM account_move_line
where name in (SELECT name FROM account_tax
		where name = 'IVA(11%) COMPRAS' and company_id in (SELECT id from res_company
								WHERE name = 'Agrinos México S.A. de C.V.')))

--"IVA(0%) COMPRAS"
UPDATE account_move_line
SET tax_id_secundary = (SELECT id FROM account_tax
			where name = 'IVA(0%) COMPRAS' and company_id in (SELECT id from res_company
									WHERE name = 'Agrinos México S.A. de C.V.'))
where id in (
SELECT id FROM account_move_line
where name in (SELECT name FROM account_tax
		where name = 'IVA(0%) COMPRAS' and company_id in (SELECT id from res_company
								WHERE name = 'Agrinos México S.A. de C.V.')))
