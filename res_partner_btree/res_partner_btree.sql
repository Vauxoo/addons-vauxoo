SELECT tabla.parent_id, sum(debit) AS debit, sum(credit) AS credit
FROM
	(
	SELECT parent.id AS parent_id, node.id AS id,node.name
	FROM res_partner AS node,res_partner AS parent
	WHERE node.parent_left BETWEEN parent.parent_left AND parent.parent_right
	ORDER BY parent.parent_left
	)tabla
JOIN
	(SELECT * FROM account_move_line)tabla2 
ON tabla.id = tabla2.partner_id
GROUP BY tabla.parent_id
