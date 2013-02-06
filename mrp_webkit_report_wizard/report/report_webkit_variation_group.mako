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
        product_uom_pool = this_self.pool.get('product.uom')
        %>
        
        <p><h3>Report of product variation group</h3></p>
        From: ${data['form'].get('date_start') or ''|entity} to: ${data['form'].get('date_finished') or ''|entity}
        <br/>For products:<br/>
            %for line in data['form'].get('product_ids'):
                <%product_data = this_self.pool.get('product.product').browse(cr, uid, line, context)%>
                ${product_data.name_template or ''|entity}
                <br>
            %endfor
        
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
        <%#Obtener los totales
        mrp_data = mrp_obj.browse(cr, uid, production_ids, context=context)
        no_children_flag = False
        %>
        <p><h4>Productions matching your query:</h4></p>
        <table class="basic_table">
            <tr>
                %for line in mrp_data:
                    %if line.subproduction_ids:
                        <td class="basic_td">
                    %else:
                        <td class="basic_td" style="color:red">
                        <%no_children_flag = True%>
                    %endif
                    ${loop.index+1 or ''|entity} - ${line.name or ''|entity}</td>
                    %if ((loop.index+1) %5 ==0):
                        </tr>
                        <tr>
                    %endif
                %endfor
            </tr>
        </table>
        %if (no_children_flag == True):
            <p class="basic_td" style="color:red">Productions marked in red don't have a subproduction children associated with them</p>
        %endif
        <br/>
        
        %if data['query_dict']:
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
        %else:
            <p>The consulted productions don't have variations</p>
        %endif

        <br/>
        %if data['finished_dict']:
            <table class="basic_table">
                <tr>
                    <td class="basic_td">Variation in finished products / details</td>
                    <th class="basic_th"> Production name </th>
                    <th class="basic_th"> Variation price </th>
                    <th class="basic_th"> Not consumed </th>
                </tr>
                
                <%row_count=1%>
                <%mrp_data = mrp_obj.browse(cr, uid, production_ids, this_context)%>
                %for production in mrp_data:
                    <%
                    total_produced = 0
                    if production.move_created_ids2:
                        for finished in production.move_created_ids2:
                            if (finished.product_id.id == production.product_id.id and finished.state in ('done')):
                                total_produced += product_uom_pool._compute_qty(cr, uid, finished.product_uom.id, finished.product_qty, to_uom_id=production.product_uom.id)
                    for subprods in production.subproduction_ids:
                        if subprods.move_lines2:
                            for consumed in subprods.move_lines2:
                                if (consumed.product_id.id == production.product_id.id and consumed.state in ('done')):
                                    total_produced -= product_uom_pool._compute_qty(cr, uid, consumed.product_uom.id, consumed.product_qty, to_uom_id=production.product_uom.id)
                    %>
                    %for variation in production.variation_finished_product_ids:
                        %if variation.quantity:
                            %if (row_count%2==0):
                                <tr  class="nonrow">
                            %else:
                                <tr>
                            %endif
                                <td class="basic_td"> ${production.product_id.name or ''|entity} </td>
                                <td class="basic_td"> ${production.name or ''|entity} </td>
                                <td class="number_td"> $ ${round(variation.cost_variation,2) or '0.0'|entity} </td>
                                <td class="number_td"> ${round(total_produced,2) or '0.0'|entity} ${production.product_uom.name or ''|entity}</td>
                            </tr>
                            <%row_count+=1%>
                        %endif
                    %endfor
                %endfor
                <tr>
                    <hr>
                </tr>
                <tr>
                    <th class="basic_th"> Reference:</th>
                    <th class="basic_th"> Quantity:</th>
                    <th class="basic_th"> Unit of M:</th>
                    <th class="basic_th"> Variation cost:</th>
                </tr>
                <%row_count=1%>
                <%total_finished_cost=0%>
                <%total_finished_qty=0%>
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
                    <%total_finished_qty+=line[1]%>
                    <%row_count+=1%>
                %endfor
                
                <%#Obtener los totales
                total_produced = 0
                total_res_dict = {}
                for production in mrp_data:
                    total_res_dict.setdefault(production.product_id.name, [0, production.product_id.uom_id.name])
                    total_produced = product_uom_pool._compute_qty(cr, uid, production.product_uom.id, production.product_qty, to_uom_id=production.product_id.uom_id.id)
                    total_res_dict[production.product_id.name][0] += total_produced
                total_produced = 0
                %>

                %for key, value in dict.items(total_res_dict):
                    <tr>
                        <td class="lastrow" style="text-align:left">Product: ${key or ''|entity}</td>
                        <td class="lastrow">Total planned to produce:</td>
                        <td class="lastrow">${value[0] or '0.00'|entity} ${value[1] or ''|entity}</td>
                        %if (len(total_res_dict) == 1):
                            <td class="lastrow">Really produced: ${value[0]+total_finished_qty or '0.00'|entity} ${value[1] or ''|entity}</td>
                        %endif
                    </tr>
                    <%total_produced += value[0]%>
                %endfor
                <tr>
                    <td class="lastrow" style="text-align:left">Production eficiency: ${100 + round(total_finished_qty*100/total_produced, 2)or '0.00'|entity} %</td>
                    <td class="lastrow">Total variation cost</td>
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
        <p style="page-break-after:always"></p>
     </body>
</html>