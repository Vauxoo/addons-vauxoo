<!DOCTYPE>
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
            %for prod in objs:
                <br>&nbsp;
                <br>&nbsp;
                <table class="basic_table">
                    <tr><td class="basic_td">Production main data</td><td class="basic_td"> &nbsp; </td><td class="basic_td"> &nbsp; </td><td class="basic_td"> &nbsp; </td></tr>
                    <tr>
                        <td class="basic_td"><b>Reference:</td>
                        <td class="basic_td">Planned quantity:</td>
                        <td class="basic_td">Date:</td>
                        <td class="basic_td">Unit of M:</td>
                    </tr>
                    <tr>
                        <td class="basic_td"><b>${prod.name or ''|entity} - ${prod.product_id.name |entity}</td>
                        <td class="basic_td">${prod.product_qty or ''|entity}</td>
                        <td class="basic_td">${prod.date_finished or ''|entity}</td>
                        <td class="basic_td">${prod.product_uom.name or ''|entity}</td>
                    </tr>
                </table>
                <br>For scheduled:
                <table class="basic_table">
                    %if prod.product_lines:
                        <tr>
                            <th class="basic_th">Product name</th>
                            <th class="basic_th">Product qty.</th>
                            <th class="basic_th">Unit of M</th>
                            <th class="basic_th">Standar price</th>
                            <th class="basic_th">Total standar price</th>
                            <th class="basic_th">Consumed Qty</th>
                            <th class="basic_th">Variation Qty</th>
                            <th class="basic_th">Variation cost</th>
                            <th class="basic_th">Variation use</th>
                        </tr>
                        <%total_c=0%>
                        <%var_use=0%>
                        <%total_var_c=0%>
                        <%row_count=1%>
                        %for line in prod.product_lines:
                            %if (row_count%2==0):
                                <tr  class="nonrow">
                            %else:
                                <tr>
                            %endif
                                <td class="basic_td">${line.product_id.name or ''|entity} </td>
                                <td class="number_td">${line.product_qty or '0.0'|entity} </td>
                                <td class="basic_td">${line.product_uom.name or ''|entity} </td>
                                <td class="number_td">$ ${line.product_id.standard_price or '0.00'|entity} </td>
                                <td class="number_td">$ ${line.product_id.standard_price*line.product_qty or '0.00'|entity} </td>
                                %if prod.variation_ids:
                                    %for var in prod.variation_ids:
                                        %if ({line.product_id.id}=={var.product_id.id}):
                                            <td class="number_td">${var.quantity+line.product_qty or '0.0'|entity} </td>
                                            <td class="number_td">${var.quantity or '0.0'|entity} </td>
                                            <td class="number_td">$ ${round(var.cost_variation,2) or '0.0'|entity} </td>
                                            <%if line.product_qty <>0:
                                                var_use=round(var.quantity*100/line.product_qty, 2)%>
                                            <td class="number_td">${var_use or '0.0'|entity} %</td>
                                            <%total_var_c+=var.cost_variation%>
                                        %endif
                                    %endfor
                                %endif
                            </tr>
                            <%total_c+=line.product_id.standard_price*line.product_qty%>
                            <%row_count+=1%>
                        %endfor
                        <tr>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow">Total:</td>
                            <td class="lastrow">$ ${total_c or '0.00'|entity}</td>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow">$ ${round(total_var_c,2) or '0.00'|entity}</td>
                        </tr>
                    %endif
                </table>
                
                <br>For finished products:
                <table class="basic_table">
                    %if prod.pt_planified_ids:
                        <tr>
                            <th class="basic_th">Product name</th>
                            <th class="basic_th">Product qty.</th>
                            <th class="basic_th">Unit of M</th>
                            <th class="basic_th">Standar price</th>
                            <th class="basic_th">Total standar price</th>
                            <th class="basic_th">Produced Qty</th>
                            <th class="basic_th">Variation Qty</th>
                            <th class="basic_th">Variation cost(-)</th>
                            <th class="basic_th">Variation use</th>
                        </tr>
                        <%total_pt_c=0%>
                        <%var_pt_use=0%>
                        <%total_var_pt_c=0%>
                        <%row_count=1%>
                        %for pt in prod.pt_planified_ids:
                            %if (row_count%2==0):
                                <tr  class="nonrow">
                            %else:
                                <tr>
                            %endif
                                <td class="basic_td">${pt.product_id.name or ''|entity} </td>
                                <td class="number_td">${pt.quantity or '0.0'|entity} </td>
                                <td class="basic_td">${pt.product_uom.name or ''|entity} </td>
                                <td class="number_td">$ ${pt.product_id.standard_price or '0.00'|entity} </td>
                                <td class="number_td">$ ${pt.product_id.standard_price*pt.quantity or '0.00'|entity} </td>
                                %if prod.variation_finished_product_ids:
                                    %for var_pt in prod.variation_finished_product_ids:
                                        %if ({pt.product_id.id}=={var_pt.product_id.id}):
                                            <td class="number_td">${var_pt.quantity+pt.quantity or '0.0'|entity} </td>
                                            <td class="number_td">${var_pt.quantity or '0.0'|entity} </td>
                                            <td class="number_td">$ ${round(var_pt.cost_variation,2) or '0.0'|entity} </td>
                                            <%if line.product_qty <>0:
                                                var_pt_use=round(var_pt.quantity*100/line.product_qty, 2)%>
                                            <td class="number_td">${var_pt_use or '0.0'|entity} %</td>
                                            <%total_var_pt_c+=var_pt.cost_variation%>
                                        %endif
                                    %endfor
                                %endif
                            </tr>
                            <%total_pt_c+=pt.product_id.standard_price*pt.quantity%>
                            <%row_count+=1%>
                        %endfor
                        <tr>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow">Total:</td>
                            <td class="lastrow">$ ${total_pt_c or '0.00'|entity}</td>
                            <td class="lastrow"></td>
                            <td class="lastrow"></td>
                            <td class="lastrow">$ ${round(total_var_pt_c,2) or '0.00'|entity}</td>
                        </tr>
                    %endif
                </table>
                
                <br/>
                <table class="basic_table">
                    %if prod.variation_finished_product_ids:
                        <tr>
                            <td class="basic_td">Variación de la producción</td>
                            <td class="number_td">$ ${round(total_var_c,2)-round(total_var_pt_c,2) or '0.00'|entity}</td>
                        </tr>
                        %endif
                </table>
                
                %if prod.superproduction_ids:
                    <br/> For superproductions:
                    <table class="basic_table">
                    <tr>
                        <td class="basic_td">#</td>
                        <td class="basic_td"><b>Reference:</td>
                        <td class="basic_td">Planned quantity:</td>
                        <td class="basic_td">Date:</td>
                        <td class="basic_td">Unit of M:</td>
                    </tr>
                    %for superps in prod.superproduction_ids:
                        <tr>
                            <td class="basic_td"><b>--</td>
                            <td class="basic_td"><b>${superps.name or ''|entity} - ${superps.product_id.name |entity}</td>
                            <td class="basic_td">${superps.product_qty or ''|entity}</td>
                            <td class="basic_td">${superps.date_finished or ''|entity}</td>
                            <td class="basic_td">${superps.product_uom.name or ''|entity}</td>
                        </tr>
                    %endfor
                    </table>
                    <br/>

                %endif
                
                %if prod.subproduction_ids:
                    <br/> For subproductions:
                    <%subps_list=[]%>
                    <table class="basic_table">
                    <tr>
                        <td class="basic_td">*</td>
                        <td class="basic_td"><b>Reference:</td>
                        <td class="basic_td">Planned quantity:</td>
                        <td class="basic_td">Date:</td>
                        <td class="basic_td">Unit of M:</td>
                    </tr>
                    %for subps in prod.subproduction_ids:
                        <%subps_list.append(subps)%>
                        <tr>
                            <td class="basic_td"><b>--</td>
                            <td class="basic_td"><b>${subps.name or ''|entity} - ${subps.product_id.name |entity}</td>
                            <td class="basic_td">${subps.product_qty or ''|entity}</td>
                            <td class="basic_td">${subps.date_finished or ''|entity}</td>
                            <td class="basic_td">${subps.product_uom.name or ''|entity}</td>
                        </tr>
                    %endfor
                    </table>
                    <br/>
                    <hr>Children production detail
                    <br/>
                    <table class="basic_table">
                        <tr>
                            <td class="basic_td">-&gt;</td>
                            <td class="basic_td">${all_prods(subps_list)}</td>
                        </tr>
                    </table>
                %endif
            %endfor
        </%def>
        
        %for obje in objects:
            ${all_prods([obje])}
            <p style="page-break-after:always"></p>
        %endfor
