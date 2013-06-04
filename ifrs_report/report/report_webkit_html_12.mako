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
					<tr><td>${ ifrs.ifrs_lines_ids[0]._get_period_print_info(data['period'],data['report_type']) }</td></tr>
				</table>
			</td>
			<td>
			<table>
				%try:
					<tr><td>${helper.embed_logo_by_name('company_logo',80,60)|n}</td></tr>
				%except:
					<tr><td></td></tr>
				%endtry
			</table>
			</td>
		</tr>
	</table> 


    <table class="list_table"  width="90%">
		<%
			period_name = ifrs.ifrs_lines_ids[0]._get_periods_name_list(o,data['fiscalyear'])
		%>
		<thead>
			<tr>
				<th class="celda_border">Descripcion</th>
				%for li in range(1, 13):
					<th class="celda">
						%try:
							${ period_name[li][2] }
						%except:
							/
						%endtry
					</th>
				%endfor
			</tr>
		</thead>
		
		%for ifrs_l in ifrs.ifrs_lines_ids:
			<%
				res = {}
				res_total = {}
				row_count = 1
			%>
			<tbody>
				
			<tr class="prueba">
				<th class="celda3">${ifrs_l.name}</th>
				%for lins in range(1, 13):
					<%
						try:
							res_total.setdefault('total_%s'%lins, 0)
							res_total['total_%s'%lins] += ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'],lins, data['target_move'])
						except:
							pass
					%>
					<td class="celda2">
						%try:
							${formatLang( ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'],lins, data['target_move']), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
						%except:
							22.22
						%endtry
					</td>
				%endfor 
			</tr>
			
			%for ifrs_al in ifrs.ifrs_lines_ids[0]._get_partner_detail(ifrs_l):
				%if ifrs_al:
					%if (row_count%2==0):
						<tr class="nonrow">
					%else:
						<tr>
					%endif
						<th class="justify">${ifrs_al.name or ''|entity}</th>
						%for lin in range(1, 13):
							<%
								try:
									res.setdefault('total_%s'%lin, 0)
									res['total_%s'%lin] += ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'], lin, data['target_move'], ifrs_al.id)
								except:
									pass
							%>
							<td class="celda_border">
								%try:
									${formatLang( ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'], lin, data['target_move'], ifrs_al.id), digits=2, date=False, date_time=False, grouping=3, monetary=False)}
								%except:
									0.0
								%endtry:
							</td>
						%endfor
					</tr>
				%endif
				<%row_count+=1%>
			%endfor
			%if ifrs_l.type != 'total':
				<tr> 
					<th class="justify">Undefined</th>
					%for line in range(1, 13):
						<%
							total_detail= abs(res.get('total_%s'%line, 0.0))
							total_period = abs(res_total.get('total_%s'%line, 0.0))
							total_undefined = total_period - total_detail
							total_undefined = abs(total_undefined)
						%>
						<td class="celda_border">${formatLang( total_undefined, digits=2, date=False, date_time=False, grouping=3, monetary=False)}</td>
					%endfor
				</tr>
			%endif
		%endfor
		</tbody>
    </table>
    %endfor
</body>
</html>
