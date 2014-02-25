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
        <% dict_data = set_dict_data(o) %>
        <table class="basic_table">
            <tr>
                <td>
                    <table class="basic_table">
                        <tr>
                            <td width='20%'>
                                %if dict_data['@tipoDeComprobante'] == 'ingreso':
                                    <div class="invoice">${_("Factura:")}
                                %elif dict_data['@tipoDeComprobante'] == 'egreso':
                                    <div class="refund">${_("NOTA DE CREDITO:")}
                                %endif
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>        
        <table class="line" width="100%" border="1"></table>
    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>
