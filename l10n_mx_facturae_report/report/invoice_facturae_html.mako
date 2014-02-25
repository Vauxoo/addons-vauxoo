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
                <td>
                    <table class="basic_table">
                        <tr>
                            <td width='50%'>
                            </td>
                        </tr> 
                        %for dic in [set_dict_data(o)]:
						<tr>
							<td class="total_td">${ dic['Conceptos']['Concepto']['@descripcion'] }</td>
						</tr>
						%endfor
                    </table>
                </td>
            </tr>
        </table>
    %endfor
</body>
</html>
