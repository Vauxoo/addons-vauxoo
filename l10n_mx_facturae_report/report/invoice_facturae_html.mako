<!DOCTYPE>
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
        <% dict_context_extra_data = o.context_extra_data and eval(o.context_extra_data) or {}%>
        <table class="basic_table">
            <tr>
                <td style="vertical-align: top;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, 85)}
                </td>
                <td style="vertical-align: top;">
                    <table class="basic_table">
                        <tr>
                            <td width="50%">
                                <div class="title">${ dict_data.get('Emisor', False) and dict_data.get('Emisor').get('@nombre', False) or ''|entity}</div>
                            </td>
                            <td width="20%">
                                <div class="invoice">
                                    %if dict_context_extra_data.get('type', False) == 'out_invoice':
                                        <font size="5">${_("Factura:")}
                                    %elif dict_context_extra_data.get('type', False) == 'out_refund':
                                        <font size="4">${_("Nota de credito:")}
                                    %endif
                                    %if dict_context_extra_data.get('type', False) in ['out_invoice', 'out_refund']:
                                        %if o.state in ['done']:
                                            ${o.document_source or ''|entity}
                                        %else:
                                            ${'SIN FOLIO O ESTATUS NO VALIDO'}
                                        %endif
                                    %elif dict_context_extra_data.get('type', False) in ['payroll']:
                                        <font size="4">${_('Payroll: ') |entity} ${o.document_source or ''|entity}</font>
                                    %endif
                                    </font>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td class="td_data_exp">
                                <div class="emitter">
                                    <%dom_fis = dict_data.get('Emisor', {}).get('DomicilioFiscal', {}) or {}%>
                                    <br/>${ dom_fis.get('@calle', False) or ''|entity}
                                    ${ dom_fis.get('@noExterior', False) or ''|entity}
                                    ${ dom_fis.get('@noInterior', False) or ''|entity}
                                    ${ dom_fis.get('@colonia', False) or ''|entity}
                                    ${ dom_fis.get('@codigoPostal', False) or ''|entity}
                                    <br/>${ _("Localidad:")} ${ dom_fis.get('@localidad', False) or ''|entity}                                    
                                    <br/>${ dom_fis.get('@municipio', False) or ''|entity}                                    
                                    , ${ dom_fis.get('@estado', False) or ''|entity}                                    
                                    , ${ dom_fis.get('@pais', False) or ''|entity}
                                    <br/><b>${_("RFC:")} ${dict_data.get('Emisor', False) and dict_data.get('Emisor').get('@rfc', False) or ''|entity}</b>
                                    <br/>${ dict_data.get('Emisor', False) and dict_data.get('Emisor').get('RegimenFiscal', False) and dict_data.get('Emisor').get('RegimenFiscal').get('@Regimen', False) or ''|entity }
                                    <%emisor = dict_context_extra_data.get('emisor', {})%>
                                    %if emisor.get('phone', False) or emisor.get('fax', False) or emisor.get('mobile', False):
                                        <br/>${_("Tel&eacute;fono(s):")}
                                        ${emisor.get('phone', False) or ''|entity}
                                        ${emisor.get('fax', False)  and ',' or ''|entity} ${emisor.get('fax', False) or ''|entity}
                                        ${emisor.get('mobile', False) and ',' or ''|entity} ${emisor.get('mobile', False) or ''|entity}
                                    %endif
                                </div>
                            </td>
                            <td class="td_data_exp">
                                <div class="fiscal_address">
                                    <br/>Expedido en:
                                        ${ dict_data.get('Emisor', False) and dict_data.get('Emisor').get('@nombre', False) or ''|entity}
                                        <%expedido = dict_data.get('Emisor', {}).get('ExpedidoEn', {}) or {}%>
                                        <br/>${ expedido.get('@calle', False) or ''|entity}
                                        ${ expedido.get('@noExterior', False) or ''|entity}
                                        ${ expedido.get('@noInterior', False) or ''|entity}
                                        ${ expedido.get('@colonia', False) or ''|entity}
                                        ${ expedido.get('@codigoPostal', False) or ''|entity}
                                        <br/>Localidad: ${ expedido.get('@localidad', False) or ''|entity}
                                        <br/>${ expedido.get('@municipio', False) or ''|entity}
                                        ${ expedido.get('@estado', False) or ''|entity}
                                        ${ expedido.get('@pais', False) or ''|entity}
                                <div/>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>        
        <table class="line" width="100%" border="1"></table>
        <table class="basic_table" style="font-size:11;">
            <tr>
                <td width="80%">
                    <table class="basic_table">
                        <tr>
                            <td class="cliente"><b>Receptor:</b></td>
                            <td width="64%" class="cliente">${ dict_data.get('Receptor', False) and dict_data.get('Receptor').get('@nombre', False) or ''|entity}</td>
                            <td class="cliente"><b>R. F. C.:</b></td>
                            <td width="16%" class="cliente"><b>${ dict_data.get('Receptor', False) and dict_data.get('Receptor').get('@rfc', False) or ''|entity}</b></td>
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="7%" class="cliente"><b>Calle:</b></td>
                            <%add_receptor = dict_data.get('Receptor', {}).get('Domicilio', {}) or {}%>
                            <td class="cliente">${ add_receptor.get('@calle') or ''|entity}</td>
                            <td width="9%" class="cliente"><b>No. Ext:</b></td>
                            <td width="9%" class="cliente">${ add_receptor.get('@noExterior', False) or ''|entity}</td>
                            <td width="9%" class="cliente"><b>No. Int:</b></td>
                            <td width="9%" class="cliente">${ add_receptor.get('@noInterior', False) or ''|entity}</td>
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="10%" class="cliente"><b>Colonia:</b></td>
                            <td class="cliente">${ add_receptor.get('@colonia', False) or ''|entity}</td>
                            <td width="7%" class="cliente"><b>C.P.:</b></td>
                            <td class="cliente">${ add_receptor.get('@codigoPostal', False) or ''|entity}</td>
                            <td width="12%" class="cliente"><b>Localidad:</b></td>
                            <td class="cliente">${ add_receptor.get('@localidad', False) or ''|entity}</td>
                        </tr>
                    </table>
                    <table class="basic_table" style="border-bottom:1px solid #002966;">
                        <tr>
                            <td width="9%" class="cliente"><b>Lugar:</b></td>
                            <td class="cliente">
                                ${ add_receptor.get('@municipio', False) or ''|entity},
                                ${ add_receptor.get('@estado', False) or ''|entity},
                                ${ add_receptor.get('@pais', False) or ''|entity}
                            </td>       
                            %if dict_data.get('Complemento',{}).get('Nomina', {}):
                                <td width="13%" class="cliente"><b>Reg. Patronal:</b></td>
                                <td class="cliente">
                                    <%reg_patr = dict_data.get('Complemento', {}).get('Nomina', {}).get('@RegistroPatronal', '')%>${ reg_patr |entity }
                                </td>
                            %endif
                        </tr>
                    </table>
                    <table class="basic_table" style="border-bottom:1px solid #002966;">
                        <tr>
                            <%receptor = dict_context_extra_data.get('receptor', False)%>
                            %if receptor and (receptor.get('phone', False) or receptor.get('fax', False) or receptor.get('mobile', False)):
                                <td width="13%" class="cliente"><b>Telefono(s):</b></td>
                                <td width="55%" class="cliente">
                                    ${receptor.get('phone', False) or ''|entity}
                                    ${receptor.get('fax', False) and ',' or ''|entity}
                                    ${receptor.get('fax', False) or ''|entity}
                                    ${receptor.get('mobile', False) and ',' or ''|entity}
                                    ${receptor.get('mobile', False) or ''|entity}</font>
                            %endif
                            %if dict_context_extra_data.get('origin', False ):
                                <td width="9%" class="cliente"><b>Origen:</b></td>
                                <td width="23%" class="cliente"><b>${dict_context_extra_data.get('origin', False) or ''|entity}</b></td>
                            %endif
                        </tr>
                    </table>
                </td>
                <td width="19%" align="center">
                    <table class="basic_table" style="text-align:center;font-size: 8pt" border="0">
                        <tr>
                            <td>
                                <b>Lugar, fecha y hora de emisión:</b>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                ${ dict_data.get('@LugarExpedicion', '') |entity}
                                <% from datetime import datetime %>
                                <br/>${_("a")} ${dict_data.get('@fecha', False) and datetime.strptime(dict_data.get('@fecha').encode('ascii','replace'), '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y %H:%M:%S') or ''|entity}
                                <br/>${_("Serie:")} ${ dict_data.get('@serie', False) or _("Sin serie")|entity}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        %if dict_data.get('Complemento',{}).get('Nomina', {}):
            <%nomina = dict_data.get('Complemento',{}).get('Nomina', {})%>
            <table width="100%">
                <table width="100%" class="basic_table" style="font-size:9; border:1.5px solid grey;">
                    <tr>                          
                        <td class="cliente"><b>${_('No. Identificaci&oacute;n')}</b></td><td class="cliente">${ nomina.get('@NumEmpleado', '') |entity }</td>
                        <td class="cliente"><b>${_('Puesto')}</b></td><td class="cliente">${ nomina.get('@Puesto', '') |entity }</td>
                        <td class="cliente"><b>${_('CURP')}</b></td><td class="cliente">${ nomina.get('@CURP', '') |entity }</td>
                    </tr>
                    <tr>
                        <td class="cliente"><b>${_('Riesgo de puesto')}</b></td><td class="cliente">${ nomina.get('@RiesgoPuesto', '') |entity }</td>
                        <td class="cliente"><b>${_('Departamento')}</b></td><td class="cliente">${ nomina.get('@Departamento', '') |entity }</td>
                        <td class="cliente"><b>${_('N&uacute;m. seguridad social')}</b></td><td class="cliente">${ nomina.get('@NumSeguridadSocial', '') |entity } </td>
                    </tr>
                </table>
            </table>
        %endif
        <br/><!-- Inicio Nodo Nomina -->
        %if dict_data.get('Complemento',{}).get('Nomina', {}):
            <table width="100%">
                <table width="100%" class="basic_table" style="font-size:12;">
                    <tr>
                        <td style="text-align:center;">
                            <b>${_('INFORMACI&Oacute;N LABORAL')}</b>
                        </td>
                    </tr>
                </table>
                </tr>
                <tr>
                    <table width="100%" class="basic_table" style="font-size:9; border:1.5px solid grey;">
                        <tr>                          
                            <td class="cliente"><b>${_('Contrato')}</b></td><td class="cliente">${ nomina.get('@TipoContrato', '') |entity }</td>
                            <td class="cliente"><b>${_('D&iacute;as Pagados')}</b></td><td class="cliente">${ nomina.get('@NumDiasPagados', '')|entity }</td>
                            <td class="cliente"><b>${_('Rel. Laboral')}</b></td><td class="cliente">${ nomina.get('@FechaInicioRelLaboral', False) and datetime.strptime(nomina.get('@FechaInicioRelLaboral').encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity }</td>
                            <td class="cliente"><b>${_('Salario diario')}</b></td><td class="cliente">${ dict_context_extra_data.get('symbol_currency', '') } ${ nomina.get('@SalarioDiarioIntegrado', '') |entity }</td>
                        </tr>
                        <tr>
                            <td class="cliente"><b>${_('Jornada')}</b></td><td class="cliente">${ nomina.get('@TipoJornada', '') |entity }</td>
                            <td class="cliente"><b>${_('Antiguedad')}</b></td><td class="cliente">${ nomina.get('@Antiguedad', '') |entity }</td>
                            <td class="cliente"><b>${_('Salario base')}</b></td><td class="cliente">${ dict_context_extra_data.get('symbol_currency', '') } ${ nomina.get('@SalarioBaseCotApor', '') |entity } </td>
                            <td class="cliente"><b>${_('Periodo')}</b></td><td class="cliente">${ nomina.get('@PeriodicidadPago', '') |entity } </td>
                        </tr>
                    </table>
                </tr>
            </table>
            <br/>
            <table width="100%">
                <table width="100%" class="basic_table" style="font-size:12;">
                    <tr>
                        <td style="text-align:center;">
                            <b>${_('PAGO')}</b>
                        </td>
                    </tr>
                </table>
                </tr>
                <tr>
                    <table width="100%" class="basic_table" style="font-size:9; border:1.5px solid grey;">
                        <tr>                          
                            <td class="cliente"><b>${_('Fecha Pago')}</b></td><td class="cliente">${nomina.get('@FechaPago', False) and datetime.strptime(nomina.get('@FechaPago').encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                            <td class="cliente"><b>${_('Fecha Inicio')}</b></td><td class="cliente">${nomina.get('@FechaInicialPago', False) and datetime.strptime(nomina.get('@FechaInicialPago').encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                            <td class="cliente"><b>${_('Fecha Fin')}</b></td><td class="cliente">${nomina.get('@FechaFinalPago', False) and datetime.strptime(nomina.get('@FechaFinalPago').encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                        </tr>
                        <tr>
                            <td class="cliente"><b>${_('CLABE')}</b></td><td class="cliente">${ nomina.get('@CLABE', '') |entity }</td>
                            <td class="cliente"><b>${_('M&eacute;todo de pago')}</b></td><td class="cliente">${ dict_data.get('@metodoDePago', '') |entity }</td>
                            <td class="cliente"><b>${_('Banco')}</b></td><td class="cliente">${ nomina.get('@Banco', '') |entity } </td>
                        </tr>
                    </table>
                </tr>
            </table>
            <br/>
            <table width="100%" style="color:#121212">
                <tr>
                    <td width="50%" valign="top">
                        <table class="basic_table">
                            <tr style="text-align:center;">
                                <td width="10%" colspan="5" style="font-size:12;"><b>${_('PERCEPCIONES')}</b></td>
                            </tr>
                            <tr class="firstrow">
                                <th width="5%">${_('Tipo')}</th>
                                <th width="10%">${_('Clave')}</th>
                                <th>${_('Concepto')}</th>
                                <th width="11%" >${_('Importe Gravado')}</th>
                                <th width="11%" >${_('Importe Exento')}</th>
                            </tr>
                            <% dict_perc =  nomina.get('Percepciones', {}).get('Percepcion', ()) %>
                            %if not isinstance(dict_perc, list):
                                <% dict_perc =  [dict_perc] %>
                            %endif
                            %for dict in range(0,len(dict_perc)):
                                <tr style="font-size:9; border:1.5px solid grey;">
                                    <td width="5%" class="basic_td"><% t_perc = dict_perc[dict].get('@TipoPercepcion', '') %>${ t_perc }</td>
                                    <td width="10%" class="basic_td"><% clave = dict_perc[dict].get('@Clave', '') %>${ clave }</td>
                                    <td class="basic_td"><% concep = dict_perc[dict].get('@Concepto', '') %>${ concep }</td>
                                    <td width="11%" class="number_td"><% i_grava = dict_perc[dict].get('@ImporteGravado', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ i_grava }</td>
                                    <td width="15%" class="number_td"><% i_exen = dict_perc[dict].get('@ImporteExento',  '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ i_exen }</td>
                                </tr>
                             %endfor
                             <tr style="font-size:9; border:1.5px solid grey;">
                                <td class="basic_td" colspan="3"><b>${_('Total Percepciones')}</b></td>
                                <td width="9%" class="number_td"><%tot_gra = nomina.get('Percepciones', {}).get('@TotalGravado', '0.0')%>${ dict_context_extra_data.get('symbol_currency', '') } ${ tot_gra |entity}</td>
                                <td width="15%" class="number_td"><%tot_ex = nomina.get('Percepciones', {}).get('@TotalExento', '0.0')%>${ dict_context_extra_data.get('symbol_currency', '') } ${ tot_ex |entity}</td>
                            </tr>
                        </table>
                    </td>
                    <td width="50%" valign="top">
                        <table class="basic_table">
                            <tr style="text-align:center;">
                                <td width="10%" colspan="5" style="font-size:12;"><b>${_('DEDUCCIONES')}</b></td>
                            </tr>
                            <tr class="firstrow">
                                <th width="5%">${_('Tipo')}</th>
                                <th width="10%">${_('Clave')}</th>
                                <th>${_('Concepto')}</th>
                                <th width="11%" >${_('Importe Gravado')}</th>
                                <th width="11%" >${_('Importe Exento')}</th>
                            </tr>
                            <% dict_deduc =  nomina.get('Deducciones', {}).get('Deduccion', ()) %>
                            %if not isinstance(dict_deduc, list):
                                <% dict_deduc =  [dict_deduc] %>
                            %endif
                            %for dict in range(0,len(dict_deduc)):
                                <tr style="font-size:9; border:1.5px solid grey;">
                                    <td width="5%" class="basic_td"><% t_deduc = dict_deduc[dict].get('@TipoDeduccion', '') %>${ t_deduc }</td>
                                    <td width="10%" class="basic_td"><% clave = dict_deduc[dict].get('@Clave', '') %>${ clave }</td>
                                    <td class="basic_td"><% concep = dict_deduc[dict].get('@Concepto', '') %>${ concep }</td>
                                    <td width="11%" class="number_td"><% i_grava = dict_deduc[dict].get('@ImporteGravado', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ i_grava }</td>
                                    <td width="15%" class="number_td"><% i_exen = dict_deduc[dict].get('@ImporteExento', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ i_exen }</td>
                                </tr>
                            %endfor
                            <tr style="font-size:9; border:1.5px solid grey;">
                                <td class="basic_td" colspan="3"><b>${_('Total Deducciones')}</b></td>
                                <td width="9%" class="number_td"><%tot_gra = nomina.get('Deducciones', {}).get('@TotalGravado', '0.0')%>${ dict_context_extra_data.get('symbol_currency', '') } ${ tot_gra|entity}</td>
                                <td width="15%" class="number_td"><%tot_ex = nomina.get('Deducciones', {}).get('@TotalExento', '0.0')%>${ dict_context_extra_data.get('symbol_currency', '') } ${ tot_ex|entity}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                <td width="50%" valign="top">
                    <table class="basic_table">
                        <tr style="text-align:center;">
                            <td width="10%" colspan="4" style="font-size:12;"><b>${_('HORAS EXTRAS')}</b></td>
                        </tr>
                        <tr class="firstrow">
                            <th width="10%">${_('Dias')}</th>
                            <th width="10%">${_('Tipo')}</th>
                            <th width="9%" >${_('Cant. de hrs')}</th>
                            <th width="9%" >${_('Importe')}</th>
                        </tr>
                        %if nomina.get('HorasExtras', False):
                            <% dict_he =  nomina.get('HorasExtras', {}).get('HorasExtra', ())%>
                            %if not isinstance(dict_he, list):
                                <% dict_he =  [dict_he] %>
                            %endif
                            %for dict in range(0,len(dict_he)):
                                <tr style="font-size:9; border:1.5px solid grey;">
                                    <td width="10%" class="basic_td"><% dias = dict_he[dict].get('@Dias', '') %>${ dias |entity}</td>
                                    <td width="10%" class="basic_td"><% tipo = dict_he[dict].get('@TipoHoras', '') %>${ tipo |entity}</td>
                                    <td width="9%" class="basic_td"><% hrs = dict_he[dict].get('@HorasExtra', '') %>${ hrs |entity}</td>
                                    <td width="10%" class="number_td"><% imp = dict_he[dict].get('@ImportePagado', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ imp |entity}</td>
                                </tr>
                            %endfor
                        %endif
                    </table>
                </td>
                <td width="50%" valign="top">
                    <table class="basic_table">
                        <tr style="text-align:center;">
                            <td width="10%" colspan="3" style="font-size:12;"><b>${_('INCAPACIDAD')}</b></td>
                        </tr>
                        <tr class="firstrow">
                            <th width="10%">${_('Dias')}</th>
                            <th width="10%">${_('Tipo')}</th>
                            <th width="9%">${_('Importe')}</th>
                        </tr>
                        %if nomina.get('Incapacidades', False):
                            <% dict_inc =  nomina.get('Incapacidades', {}).get('Incapacidad', ()) %>
                            %if not isinstance(dict_inc, list):
                                <% dict_inc =  [dict_inc] %>
                            %endif
                            %for dict in range(0,len(dict_inc)):
                                <tr style="font-size:9; border:1.5px solid grey;">
                                    <td width="10%" class="basic_td"><% dias = dict_inc[dict].get('@DiasIncapacidad', '') %>${ dias |entity}</td>
                                    <td width="10%" class="basic_td"><% tipo = dict_inc[dict].get('@TipoIncapacidad', '') %>${ tipo |entity}</td>
                                    <td width="9%" class="number_td"><% desc = dict_inc[dict].get('@Descuento', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ desc |entity}</td>
                                </tr>
                            %endfor
                        %endif
                    </table>
                </td>
            </tr>
        </table>
        </br>
        %endif
        <!-- Fin Nodo Nomina -->
        <table class="basic_table" style="color:#121212">
            <tr class="firstrow">
                <th width="10%">${_("Cant.")}</th>
                <th width="10%">${_("Unidad")}</th>
                <th>${_("Descripci&oacute;n")}</th>
                <th width="9%" >${_("P.Unitario")}</th>
                <th width="15%">${_("Importe")}</th>
            </tr>
            <%row_count = 1%>
            <% dict_lines =  dict_data.get('Conceptos', {}).get('Concepto', ())%>
            %if not isinstance(dict_lines, list):
                <% dict_lines =  [dict_lines]%>
            %endif
            %for dict in range(0,len(dict_lines)):
                %if (row_count%2==0):
                    <tr  class="nonrow">
                %else:
                    <tr>
                %endif
                    <td width="10%" class="number_td"><% qty = dict_lines[dict].get('@cantidad', '0.0') %>${ qty |entity}</td>
                    <td width="10%" class="basic_td"><% uni = dict_lines[dict].get('@unidad', '0.0') %>${ uni |entity}</td>
                    <td class="basic_td"><% desc = dict_lines[dict].get('@descripcion', '0.0') %>${ desc |entity}</td>
                    <td width="9%" class="number_td"><% vuni = dict_lines[dict].get('@valorUnitario', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ vuni |entity}</td>
                    <td width="15%" class="number_td"><% imp = dict_lines[dict].get('@importe', '0.0') %>${ dict_context_extra_data.get('symbol_currency', '') } ${ imp |entity}</td>
                    </tr>
                <%row_count+=1%>
            %endfor
        </table>
        <table align="right" width="30%" style="border-collapse:collapse">
            <tr>
                <td class="total_td">${_("Sub Total:")}</td>
                <td align="right" class="total_td">${ dict_context_extra_data.get('symbol_currency', '') } ${ dict_data.get('@subTotal', '')|entity}</td>
            </tr>
            <% desc_amount = float(dict_data.get('@descuento', 0.0)) %>
            %if desc_amount > 0:
            <tr>
                <td class="total_td">${_("Descuento:")}</td>
                <td align="right" class="total_td">${ dict_context_extra_data.get('symbol_currency', '') } ${ dict_data.get('@descuento', '') |entity}</td>
            </tr>
            %endif
            %if dict_data.get('Impuestos', {}).get('Traslados', False):
                <% dict_imp =  dict_data.get('Impuestos', {}).get('Traslados', {}).get('Traslado', ())%>
                %if not isinstance(dict_imp, list):
                    <% dict_imp =  [dict_imp]%>
                %endif
                %for imp in range(0,len(dict_imp)):
                    <% imp_amount = float(dict_imp[imp]['@importe']) %>
                    %if imp_amount > 0:
                        <tr>
                            <td class="tax_td">
                                <% imp_name = dict_imp[imp]['@impuesto'] %>
                                <% tasa = dict_imp[imp]['@tasa'] %>
                                <% text = imp_name+' ('+tasa+') %' %>${ text or '0.0'}
                            </td>
                            <td class="tax_td" align="right">
                                ${ dict_context_extra_data.get('symbol_currency', '') } ${imp_amount or '0.0'|entity}
                            </td>
                        </tr>
                    %endif
                %endfor
            %endif
            %if dict_data.get('Impuestos', {}).get('Retenciones', False):
                <% dict_ret =  dict_data.get('Impuestos', {}).get('Retenciones', {}).get('Retencion', ())%>
                %if not isinstance(dict_ret, list):
                    <% dict_ret =  [dict_ret]%>
                %endif
                %for ret in range(0,len(dict_ret)):
                    <% ret_amount = float(dict_ret[ret]['@importe']) %>
                    %if ret_amount > 0:
                        <tr>
                            <td class="tax_td">
                                <% ret_name = dict_ret[ret]['@impuesto'] %>
                                ${_("Ret. ")} ${ ret_name or '' | entity }
                            </td>
                            <td class="tax_td" align="right">
                                ${ dict_context_extra_data.get('symbol_currency', '') } ${ ret_amount or '' | entity }
                            </td>
                        </tr>
                    %endif
                %endfor
            %endif
            <tr align="left">
                <td class="total_td"><b>${_("Total:")}</b></td>
                <td class="total_td" align="right"><b>${ dict_context_extra_data.get('symbol_currency', '') } ${ dict_data.get('@total', '')|entity}</b></td>
            </tr>
        </table>
        <table class="basic_table">
            <tr>
                <td class="tax_td">
                    ${_("IMPORTE CON LETRA:")}
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    <% amount_in_text = amount_to_text(float(dict_data.get('@total', 0.0).encode('ascii','replace')),dict_data.get('@Moneda', '')) %>
                    <i>${ amount_in_text or ''|entity}</i>
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    ${_('PAGO EN UNA SOLA EXHIBICI&Oacute;N - EFECTOS FISCALES AL PAGO')}
                </td>
            </tr>            
        </table>
        %if dict_context_extra_data.get('payment_term', False) or dict_context_extra_data.get('comment', False):
            <table class="basic_table">
                %if dict_context_extra_data.get('payment_term', False):
                    <tr>
                        %if dict_context_extra_data.get('payment_term', False):
                            <td width="100%"><pre><font size="1"><b>Condición de pago:</b> ${dict_context_extra_data.get('payment_term', False) or '' |entity}
                            </font></pre></td>
                        %endif
                    </tr>
                %endif
                %if dict_context_extra_data.get('comment', False):
                    <tr>
                        %if dict_context_extra_data.get('comment', False):
                            <td width="100%"><pre><font size="1"><b>Comentarios adicionales:</b> ${dict_context_extra_data.get('comment', False) or '' |entity}</font></pre></td>
                        %endif
                    </tr>
                %endif
            </table>
        %endif
        <pre>
            <p><font size="1">${ get_text_promissory(o.model_source, o.id_source) or '' |entity }</font></p>
        </pre>
        </br>
        %if dict_data.get('Complemento', {}).get('TimbreFiscalDigital'):
            <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                    <tr>
                        <th width="33%"> ${_('Certificado del SAT')}</th>
                        <th> ${_('Fecha de Timbrado')}</th>
                        <th width="33%"> ${_('Folio Fiscal')}</th>
                    </tr>
                    <tr>
                        <td width="33%" class="center_td"> <%tfd = dict_data.get('Complemento', {}).get('TimbreFiscalDigital', {})%>${ tfd.get('@noCertificadoSAT', 'No identificado') or 'No identificado'|entity }</td>
                        <td width="34%" class="center_td"> ${ tfd.get('@FechaTimbrado', False) and datetime.strptime(tfd.get('@FechaTimbrado').encode('ascii','replace'), '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y %H:%M:%S') or 'No identificado'|entity }</td>
                        <td width="33%" class="center_td"> ${ tfd.get('@UUID', 'No identificado')|entity }</td>
                    </tr>
            </table>
        %endif
        <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                <tr>
                    <th width="33%">${_('Certificado del emisor')}</th>
                    <th width="34%">${_('M&eacute;todo de Pago')}</th>
                    <th width="33%">${_('&Uacute;ltimos 4 d&iacute;gitos de la cuenta bancaria')}</th>
                </tr>
                <tr>
                    <td class="center_td">${ dict_data.get('@noCertificado', 'No identificado')|entity }</td>
                    <td class="center_td">${ dict_data.get('@metodoDePago', 'No identificado')|entity }</td>
                    <td class="center_td">${ dict_data.get('@NumCtaPago', 'No identificado')|entity }</td>
                </tr>
        </table>
        %if dict_data.get('Complemento', {}).get('TimbreFiscalDigital'):
            <div style="page-break-inside:avoid; border:1.5px solid grey;">
                <table width="100%" class="datos_fiscales">
                    <tr>
                        <td align="left" rowspan="2">
                            ${helper.embed_image('jpeg',str(o.company_id.cif_file), 140, 220)}
                        </td>
                        <td valign="top" align="left">
                            <p class="cadena_with_cbb_cfd">
                            <b>${_('Sello Digital Emisor:')} </b><br/>
                            ${ dict_data.get('@sello', '')|entity}<br/>
                            <b>${_('Sello Digital SAT:')} </b><br/>
                            ${ dict_data.get('Complemento').get('TimbreFiscalDigital').get('@selloSAT', '')|entity}<br/>
                            <b>${_('Cadena original:')} </b><br/>
                            ${o.cfdi_cadena_original or ''|entity}</br>
                            <b>${_('Enlace al certificado: ')}</b></br>
                            ${o.certificate_link or ''|entity}</br>
                            </p>
                        </td>
                        <td align="right" rowspan="2">
                            <% img = create_qrcode(dict_data.get('Emisor', {}).get('@rfc', ''), dict_data.get('Receptor', {}).get('@rfc', ''), float(dict_data.get('@total', 0.0).encode('ascii','replace')), dict_data.get('Complemento', {}).get('TimbreFiscalDigital', {}).get('@UUID', '')) %>
                            ${helper.embed_image('jpeg',str(img),180, 180)}
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align: center; text-align: center">
                            <p><b><font size="1">"Este documento es una representación impresa de un CFDI”</br>
                            CFDI, Comprobante Fiscal Digital por Internet</font></b></p>
                        </td>
                    </tr>
                </table>
            </div>
        %endif
        <p style="page-break-after:always"></p>
    %endfor
</body>
</html>
