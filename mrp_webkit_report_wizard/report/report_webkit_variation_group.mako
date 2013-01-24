<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <div class="basic_header">
            <table class="basic_table">
                <tr><td style="text-align:center;">${helper.embed_logo_by_name('company_logo',75, 53)|n}</td>
                <td class="basic_td">
                    <table class="basic_table">
                        <tr><td class="basic_td">Company: ${company.name |entity}</td></tr>
                        <tr><td class="basic_td">Address: ${company.partner_id.address and company.partner_id.address[0].street or ''|entity}</td></tr>
                        <tr><td class="basic_td">Phone: ${company.partner_id.address and company.partner_id.address[0].phone or ''|entity}</td></tr>
                        <tr><td class="basic_td">Mail: ${company.partner_id.address and company.partner_id.address[0].email or ''|entity}</td></tr>
                        <tr><td class="basic_td">User: ${user.name or ''|entity}</td></tr>
                    </table>
                </td></tr>
            </table>
        </div>
        
        <p><h3>Report of product variation group</h3></p>
        <table class="basic_table">
            <tr>
                <td class="basic_td">Variation in consumed products</td>
                <td class="basic_td"> &nbsp; </td>
                <td class="basic_td"> &nbsp; </td>
                <td class="basic_td"> &nbsp; </td>
            </tr>
            <tr>
                <td class="basic_td"> <b>Reference:</b></td>
                <td class="basic_td"> Quantity:</td>
                <td class="basic_td"> Unit of M:</td>
                <td class="basic_td"> Variation cost:</td>
            </tr>
            <%row_count=1%>
            <%total_consumed_cost=0%>
            %for line in data['query_dict']:
                %if (row_count%2==0):
                    <tr  class="nonrow">
                %else:
                    <tr>
                %endif
                    <td class="basic_td"> ${line[0] or ''|entity}</td>
                    <td class="number_td"> ${line[1] or '0.0'|entity}</td>
                    <td class="basic_td"> ${line[2] or ''|entity}</td>
                    <td class="number_td"> $ ${round(line[3],2) or '0.00'|entity}</td>
                </tr>
            <%total_consumed_cost+=line[3]%>
            <%row_count+=1%>
            %endfor
            <tr>
                <td class="lastrow"></td>
                <td class="lastrow">Total:</td>
                <td class="lastrow"></td>
                <td class="lastrow">$ ${round(total_consumed_cost,2) or '0.00'|entity}</td>
            </tr>
        </table>
        <br/>
        <p style="page-break-after:always"></p>
     </body>
</html>