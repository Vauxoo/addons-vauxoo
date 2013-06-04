<html xmlns="http://www.w3.org/TR/REC-html40" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
<head>
	
    <style type="text/css">
        ${css}
       
    </style>
<table>
	<tr>
		
<td width="30%" rowspan="5"><b>Reporte Impreso en OpenErp con Webkit</b></td>
<td width="30%" rowspan="5"><b>Fecha de Impresi&oacute;n:${formatLang(time.strftime('%Y-%m-%d'),date=True)} ${time.strftime('%H:%m')}</b></td>
</tr>
</table>
</head>


<body style="border:0; margin: 0;" onload="subst()" >
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

<table class="list_table" width="90%">
    <%
        period_name = ifrs.ifrs_lines_ids[0]._get_periods_name_list(data['fiscalyear'])
    %>
    
	 %for ifrs_l in ifrs.ifrs_lines_ids:
	<tbody>
		 %if not ifrs_l.invisible:
			<td>
				${ifrs_l.name}
			</td>
			<td>
				${ifrs_l.type=='detail' and formatLang( ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'], data['exchange_date'], data['period'], two=True), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
			</td>
			<td>
				${ifrs_l.type=='total' and  formatLang( ifrs.ifrs_lines_ids[0]._get_amount_value(ifrs_l, period_name, data['fiscalyear'], data['exchange_date'], data['period'], two=True), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
			</td>
		  %endif


	</tbody>
	%endfor
</table>

    %endfor
</body>
</html>
