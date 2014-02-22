<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        ${set_global_data(o)}
        <table class="basic_table">
            <tr>
                <td style="vertical-align: top;">
<!--
                    ${helper.embed_image('jpeg',str(o.company_emitter_id.logo),180, 85)}
-->
                </td>
                <td>
                    <table class="basic_table">
                        <tr>
                            <td width='50%'>
<!--
                                <div class="title">${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
-->
                            </td>
                        </tr>
<!--
                        %for dic in [set_dict_data(o.id)]:
						<tr>
							<td class="total_td">${ dic['Conceptos']['Concepto']['@descripcion'] }</td>
						</tr>
						%endfor
-->
                    </table>
                </td>
            </tr>
        </table>
    %endfor

</body>
</html>
