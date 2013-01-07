<html>
<head>
    <style type="text/css">
        ${css}
    </style>

</head>

<body style="border:0; margin: 0;" onload="subst()">
    %for ifrs in objects :
	<table>
		<tr>
			<td>
				<table class="dest_address " style="border-bottom: 0px solid black; width: 100%">
					<tr><td><b>[${ifrs.code or ''|entity}] ${ifrs.name or ''|entity}</b></td></tr>
					<tr><td>${ifrs.company_id.name or ''|entity}</td></tr>
					<tr><td>${ifrs.fiscalyear_id.name or ''|entity}</td></tr>
					<tr><td>${ get_period_print_info(data['period'],data['report_type']) }</td></tr>
				</table>
			</td>
			<td>
			<table>
				%try:
					<tr><td>${helper.embed_logo_by_name('foam',80,60)|n}</td></tr>
				%except:
					<tr><td></td></tr>
				%endtry
			</table>
			</td>
		</tr>
    </table> 


    <table class="list_table"  width="90%">
		<%
        get_periods_name_list(o,data['fiscalyear'])
        %>
        <thead>
			<tr>
				<th class="celda_border">Descripcion</th>
				%try:
					<th class="celda">${ get_column_name(1) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(2) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(3) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(4) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(5) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(6) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(7) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(8) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry				
				%try:
					<th class="celda">${ get_column_name(9) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(10) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(11) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
				%try:
					<th class="celda">${ get_column_name(12) }</th>
				%except:
					<th class="celda">0.0</th>
				%endtry
			</tr>
		</thead>
		%for ifrs_l in ifrs.ifrs_lines_ids:
		<tbody>
		<tr class="prueba">
			<th class="celda3">${ifrs_l.name}</th>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 1, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 2, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 3, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						5.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 4, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						5.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 5, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						6.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 6, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 7, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 8, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 9, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 10, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 11, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>
			<td class="celda2">
					%try:
						${formatLang( get_amount_value(ifrs_l, 12, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
					%except:
						0.0
					%endtry
			</td>

        </tr>
			%for ifrs_al in get_partner_detail(ifrs_l):
				%if ifrs_al:
					<tr>
						<th class="justify">${ifrs_al.name or ''|entity}</th>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 1, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 2, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 3, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 4, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 5, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 6, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 7, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 8, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 9, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 10, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 11, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
						<td class="celda_border">
							%try:
								${formatLang( get_amount_value(ifrs_l, 12, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
							%except:
								0.0
							%endtry:
						</td>
					</tr>
				%endif
			%endfor
		%endfor
		</tbody>
    </table>
    %endfor
</body>
</html>
