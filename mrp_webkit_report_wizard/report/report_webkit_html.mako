<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <div class="sys_header">
                    <img src="/home/kyon/openerp/instancias/6.1/addons_all/Desarrollos/report_mrp/mrp_report_webkit_test/report/LogoSys" width="149.5" height="106" />
                    ${company.name |entity}<br/>
                    ${company.partner_id.address and company.partner_id.address[0].street or ''|entity}<br/>
                    Phone: ${company.partner_id.address and company.partner_id.address[0].phone or ''|entity}<br/>
                    Mail: ${company.partner_id.address and company.partner_id.address[0].email or ''|entity}<br/>
                    User: ${user.name or ''|entity}<br/>
                </div>
                <p><h3>Reporte de variación en producciones</h3></p>

        <%def name="all_prods(objs=None)">
            %for prod in objs:
                <br>&nbsp;
                <br>&nbsp;
                <table class="basic_table">
                    <tr><td class="sys_td">Production main data</td><td class="sys_td"> &nbsp; </td><td class="sys_td"> &nbsp; </td><td class="sys_td"> &nbsp; </td></tr>
                    <tr>
                        <td class="sys_td"><b>Reference:</td>
                        <td class="sys_td">Planned quantity:</td>
                        <td class="sys_td">Date:</td>
                        <td class="sys_td">Unit of M:</td>
                    </tr>
                    <tr>
                        <td class="sys_td"><b>${prod.name or ''|entity} - ${prod.product_id.name |entity}</td>
                        <td class="sys_td">${prod.product_qty or ''|entity}</td>
                        <td class="sys_td">${prod.date_planned or ''|entity}</td>
                        <td class="sys_td">${prod.product_uom.name or ''|entity}</td>
                    </tr>
                </table>
                <br>For scheduled:
                <table class="basic_table">
                    %if prod.product_lines:
                        <tr>
                            <th class="sys_th">Product name</th>
                            <th class="sys_th">Product qty.</th>
                            <th class="sys_th">Unit of M</th>
                            <th class="sys_th">Standar price</th>
                            <th class="sys_th">Total standar price</th>
                            <th class="sys_th">Consumed Qty</th>
                            <th class="sys_th">Variation Qty</th>
                            <th class="sys_th">Variation cost</th>
                            <th class="sys_th">Variation use</th>
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
                                <td class="sys_td">${line.product_id.name or ''|entity} </td>
                                <td class="leftred">${line.product_qty or '0.0'|entity} </td>
                                <td class="sys_td">${line.product_uom.name or ''|entity} </td>
                                <td class="leftred">$ ${line.product_id.standard_price or '0.00'|entity} </td>
                                <td class="leftred">$ ${line.product_id.standard_price*line.product_qty or '0.00'|entity} </td>
                                %if prod.variation_ids:
                                    %for var in prod.variation_ids:
                                        %if ({line.product_id.id}=={var.product_id.id}):
                                            <td class="leftred">${var.quantity+line.product_qty or '0.0'|entity} </td>
                                            <td class="leftred">${var.quantity or '0.0'|entity} </td>
                                            <td class="leftred">$ ${round(var.cost_variation,2) or '0.0'|entity} </td>
                                            <%if line.product_qty <>0:
                                                var_use=round(var.quantity*100/line.product_qty, 2)%>
                                            <td class="leftred">${var_use or '0.0'|entity} %</td>
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
                            <th class="sys_th">Product name</th>
                            <th class="sys_th">Product qty.</th>
                            <th class="sys_th">Unit of M</th>
                            <th class="sys_th">Standar price</th>
                            <th class="sys_th">Total standar price</th>
                            <th class="sys_th">Produced Qty</th>
                            <th class="sys_th">Variation Qty</th>
                            <th class="sys_th">Variation cost(-)</th>
                            <th class="sys_th">Variation use</th>
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
                                <td class="sys_td">${pt.product_id.name or ''|entity} </td>
                                <td class="leftred">${pt.quantity or '0.0'|entity} </td>
                                <td class="sys_td">${pt.product_uom.name or ''|entity} </td>
                                <td class="leftred">$ ${pt.product_id.standard_price or '0.00'|entity} </td>
                                <td class="leftred">$ ${pt.product_id.standard_price*pt.quantity or '0.00'|entity} </td>
                                %if prod.variation_finished_product_ids:
                                    %for var_pt in prod.variation_finished_product_ids:
                                        %if ({pt.product_id.id}=={var_pt.product_id.id}):
                                            <td class="leftred">${var_pt.quantity+pt.quantity or '0.0'|entity} </td>
                                            <td class="leftred">${var_pt.quantity or '0.0'|entity} </td>
                                            <td class="leftred">$ ${round(var_pt.cost_variation,2) or '0.0'|entity} </td>
                                            <%if line.product_qty <>0:
                                                var_pt_use=round(var_pt.quantity*100/line.product_qty, 2)%>
                                            <td class="leftred">${var_pt_use or '0.0'|entity} %</td>
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
                            <td class="sys_td">Variación de la producción</td>
                            <td class="leftred">$ ${round(total_var_pt_c,2)-round(total_var_c,2) or '0.00'|entity}</td>
                        </tr>
                        %endif
                </table>
                
                %if prod.subproduction_ids:
                    <br/> For subproductions:
                    <table class="basic_table">
                    <tr>
                        <td class="sys_td">*</td>
                        <td class="sys_td"><b>Reference:</td>
                        <td class="sys_td">Planned quantity:</td>
                        <td class="sys_td">Date:</td>
                        <td class="sys_td">Unit of M:</td>
                    </tr>
                    %for subps in prod.subproduction_ids:
                        <tr>
                            <td class="sys_td"><b>--</td>
                            <td class="sys_td"><b>${subps.name or ''|entity} - ${subps.product_id.name |entity}</td>
                            <td class="sys_td">${subps.product_qty or ''|entity}</td>
                            <td class="sys_td">${subps.date_planned or ''|entity}</td>
                            <td class="sys_td">${subps.product_uom.name or ''|entity}</td>
                        </tr>
                    %endfor
                    </table>
                    <br/>
                %endif
                
                %if prod.superproduction_ids:
                    <br/> For superproductions:
                    <%superps_list=[]%>
                    <table class="basic_table">
                    <tr>
                        <td class="sys_td">#</td>
                        <td class="sys_td"><b>Reference:</td>
                        <td class="sys_td">Planned quantity:</td>
                        <td class="sys_td">Date:</td>
                        <td class="sys_td">Unit of M:</td>
                    </tr>
                    %for superps in prod.superproduction_ids:
                        <%superps_list.append(superps)%>
                        <tr>
                            <td class="sys_td"><b>--</td>
                            <td class="sys_td"><b>${superps.name or ''|entity} - ${superps.product_id.name |entity}</td>
                            <td class="sys_td">${superps.product_qty or ''|entity}</td>
                            <td class="sys_td">${superps.date_planned or ''|entity}</td>
                            <td class="sys_td">${superps.product_uom.name or ''|entity}</td>
                        </tr>
                    %endfor
                    </table>
                    <br/>

                    <hr>Detalle de producciones hijas
                    <br/>
                    <table class="basic_table">
                        <tr>
                            <td class="sys_td">-&gt;</td>
                            <td class="leftred">${all_prods(superps_list)}</td>
                        </tr>
					</table>
                %endif
            %endfor
        </%def>
        %for obje in objects:
			${all_prods([obje])}
			<p style="page-break-after:always"></p>
		%endfor
        
    </body>
</html>
