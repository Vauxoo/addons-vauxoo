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
        
        <%
        wiz_user = this_self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', wiz_user.company_id.id)
        mrp_obj = this_self.pool.get('mrp.production')
        %>
        
        <p><h3>Report of product variation group</h3></p>
        From: ${data['form'].get('date_start') or ''|entity} to: ${data['form'].get('date_finished') or ''|entity}
        <br/>For products:
            %for line in data['form'].get('product_ids'):
                <%
                mrp_data = mrp_obj.browse(cr, uid, line, context)
                print mrp_data.product_id.name, "mrp data"
                %>
                ${mrp_data.product_id.name or ''|entity}
                <br>
            %endfor
        <table class="basic_table">
            <tr>
                <td class="basic_td">Variation in consumed products</td>
                <td class="basic_td"> &nbsp; </td>
                <td class="basic_td"> &nbsp; </td>
                <td class="basic_td"> &nbsp; </td>
            </tr>
        
            <tr>
                <th class="basic_th"> Reference:</th>
                <th class="basic_th"> Quantity:</th>
                <th class="basic_th"> Unit of M:</th>
                <th class="basic_th"> Variation cost:</th>
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
        %if data['finished_dict']:
            <table class="basic_table">
                <tr>
                    <td class="basic_td">Variation in finished products</td>
                    <th class="basic_th"> Detailed </th>
                    <th class="basic_th"> Production name </th>
                    <th class="basic_th"> Variation price </th>
                </tr>
                
                <%
                production_ids = mrp_obj.search(cr, uid , [('state', 'not in', ('draft', 'cancel')), \
                    ('product_id', 'in', data['form']['product_ids']), ('date_planned', '>', data['form']['date_start']), \
                    ('date_planned', '<', data['form']['date_finished']), ('company_id', '=', company_id)])
                cr.execute("""
SELECT mrp_variation_finished_product.product_id, mrp_production.name ,standard_price * quantity AS mul, name_template FROM mrp_variation_finished_product
INNER JOIN mrp_production
  ON mrp_production.id = mrp_variation_finished_product.production_id
INNER JOIN product_product
  ON product_product.id = mrp_variation_finished_product.product_id
INNER JOIN product_template
  ON product_template.id = product_product.product_tmpl_id
WHERE production_id IN 
%s
ORDER BY mul
                """, (tuple(production_ids),))

                records = cr.fetchall()
                %>
                
                <%row_count=1%>
                %for line in records:
                    %if (row_count%2==0):
                        <tr  class="nonrow">
                    %else:
                        <tr>
                    %endif
                        <td class="basic_td"> &nbsp; </td>
                        <td class="basic_td"> ${line[3] or ''|entity} </td>
                        <td class="basic_td"> ${line[1] or '0.0'|entity}</td>
                        <td class="number_td"> $ ${round(line[2],2) or '0.0'|entity}</td>
                    </tr>
                <%row_count+=1%>
                %endfor
                
                <tr>
                    <th class="basic_th"> Reference:</th>
                    <th class="basic_th"> Quantity:</th>
                    <th class="basic_th"> Unit of M:</th>
                    <th class="basic_th"> Variation cost:</th>
                </tr>
                <%row_count=1%>
                <%total_finished_cost=0%>
                %for line in data['finished_dict']:
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
                <%total_finished_cost+=line[3]%>
                <%row_count+=1%>
                %endfor
                <tr>
                    <td class="lastrow"></td>
                    <td class="lastrow">Total:</td>
                    <td class="lastrow"></td>
                    <td class="lastrow">$ ${round(total_finished_cost,2) or '0.00'|entity}</td>
                </tr>
            </table>
        %endif
        
        <br/>
        %if data['child_consumed']:
            <hr/>
            <table class="basic_table">
                <tr>
                    <td class="basic_td">Variation in children consumed products</td>
                    <td class="basic_td"> &nbsp; </td>
                    <td class="basic_td"> &nbsp; </td>
                    <td class="basic_td"> &nbsp; </td>
                </tr>
                <tr>
                    <th class="basic_th"> Reference:</th>
                    <th class="basic_th"> Quantity:</th>
                    <th class="basic_th"> Unit of M:</th>
                    <th class="basic_th"> Variation cost:</th>
                </tr>
                <%row_count=1%>
                <%total_child_consumed_cost=0%>
                %for line in data['child_consumed']:
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
                <%total_child_consumed_cost+=line[3]%>
                <%row_count+=1%>
                %endfor
                <tr>
                    <td class="lastrow"></td>
                    <td class="lastrow">Total:</td>
                    <td class="lastrow"></td>
                    <td class="lastrow">$ ${round(total_child_consumed_cost,2) or '0.00'|entity}</td>
                </tr>
            </table>
        %endif
        
        <br/>
        %if data['child_finished']:
            <table class="basic_table">
                <tr>
                    <td class="basic_td">Variation in children finished products</td>
                    <td class="basic_td"> &nbsp; </td>
                    <td class="basic_td"> &nbsp; </td>
                    <td class="basic_td"> &nbsp; </td>
                </tr>
                <tr>
                    <th class="basic_th"> Reference:</th>
                    <th class="basic_th"> Quantity:</th>
                    <th class="basic_th"> Unit of M:</th>
                    <th class="basic_th"> Variation cost:</th>
                </tr>
                <%row_count=1%>
                <%total_child_finished_cost=0%>
                %for line in data['child_finished']:
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
                <%total_child_finished_cost+=line[3]%>
                <%row_count+=1%>
                %endfor
                <tr>
                    <td class="lastrow"></td>
                    <td class="lastrow">Total:</td>
                    <td class="lastrow"></td>
                    <td class="lastrow">$ ${round(total_child_finished_cost,2) or '0.00'|entity}</td>
                </tr>
            </table>
        %endif
        
        <br/>
        
        <br/>
        <p style="page-break-after:always"></p>
     </body>
</html>