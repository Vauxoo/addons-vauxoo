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
         <p><h3>Report of product variation</h3></p>

        <%def name="all_prods(objs=None)">
            llamando funcion
        <%unique_ids=[]%>
        <%all_prod_ids=get_all_ids()%>
        <%mySet = set(all_prod_ids)%>
        <%unique_ids = list(mySet)%>
        <br>
        imprimo unique_ids, son browses <br>${unique_ids or '[]'|entity}
        
        <%group_dict = {}%>
        <%dict_data = {}%>
        %for line in unique_ids:
            <%
            dict_data.update({
                'name' : line.name,
                'product_id' : line.product_id.id,
                'product_qty' : line.product_qty,
                'product_uom' : line.product_id.uom_id.id,
                'prod_variat' : 'var_pt',
            })
            group_dict.setdefault(line.id, dict_data)
            dict_data = {}
            %>
        %endfor
        <%print group_dict, "g di"%>
        
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
    </body>
</html>

for line in dict:
    subdict = dict.get(line)
    pid = subdict.get('product_id')
    print pid
        </%def>
        
        %for obje in objects:
            ${all_prods([obje])}
            <p style="page-break-after:always"></p>
        %endfor
        
        <%def name="get_all_ids()">
            <%all_ids=[]%>
            %for o in objects:
                <br> ${o.id or ''|entity} renglon
                <%all_ids.append(o)%>
                %if o.subproduction_ids:
                    %for subps in o.subproduction_ids:
                        <%all_ids.append(subps)%>
                        %if subps.subproduction_ids:
                            %for sublvl2 in subps.subproduction_ids:
                                <%all_ids.append(sublvl2)%>
                            %endfor
                        %endif
                    %endfor
                %endif
            %endfor
            <br>
            imprimo all_ids ${all_ids or '[]'|entity}
            <%return all_ids%>
        </%def>