<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body style="border:0; margin: 0;" onload="subst()" >
        %for obj in objects :
            <table>
                <tr>
                    <td width="30%">
                        <div>${helper.embed_image('jpeg',str(obj.company_id.logo),260, 120)}</div>
                    </td>
                    <td>
                        <table style="width: 100%; text-align:center;">
                            <tr><td><div class="td_company_title">${obj.company_id.name or ''|entity}</div></td></tr>
                            <tr><td><div class="td_company">${obj.fiscalyear_id.name or ''|entity}</div></td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            <br clear="all"/>
            
            <table class="list_table"  width="100%" border="0">
                <thead>
                    <tr>
                        <th class="celdaTituloTabla" width="100%">(Expressed in ${obj.company_id.currency_id.name |entity} )</th>
                    </tr>
                </thead>
            </table>
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    %for line in obj.partner_line_ids:
                        <tr class="prueba" >
                            <td class="celdaTotalTitulo" width="30%">
                                ${line.partner_id.name.upper()}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.not_due}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.days_due_01to30}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.days_due_31to60}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.days_due_61to90}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.days_due_91to120}
                            </td>
                            <td class="celdaTotalTitulo" width="10%">
                                ${line.days_due_121togr}
                            </td>
                    %endfor
                </tbody>
            </table>
        %endfor
    </body>
</html>
