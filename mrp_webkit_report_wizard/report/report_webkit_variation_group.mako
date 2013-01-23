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
     </body>
</html>

        <%def name="all_prods(objs=None)">
            llamando funcion
        
        <table class="basic_table">
            <tr><td class="basic_td">Production main data</td><td class="basic_td"> &nbsp; </td><td class="basic_td"> &nbsp; </td><td class="basic_td"> &nbsp; </td></tr>
            <tr>
                <td class="basic_td"><b>Reference:</td>
                <td class="basic_td">Planned quantity:</td>
                <td class="basic_td">Date:</td>
                <td class="basic_td">Unit of M:</td>
            </tr>
            <tr>
                <td class="basic_td"><b>a</td>
            </tr>
        </table>
        dict_data: ${dict_data or ''|entity}
        group_dict: ${group_dict or ''|entity}

for line in dict:
    subdict = dict.get(line)
    pid = subdict.get('product_id')
    print pid
        </%def>
        
        %for obje in objects:
            ${all_prods([obje])}
            <p style="page-break-after:always"></p>
        %endfor
        