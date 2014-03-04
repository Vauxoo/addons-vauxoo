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
                <td style="vertical-align: top;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, 85)}
                </td>
                <td>
                    <table class="basic_table">
                        <tr>
                            <td width='50%'>
                                <div class="title">${ dict_data['Emisor']['@nombre'] or ''|entity}</div>
                            </td>
                            <td width='20%'>
                                <div class="invoice">${_("Documento:")}
                                ${o.document_source or ''|entity}
                            </td>
                        </tr>
                        <tr>
                            <td class="td_data_exp">
                                <div class="emitter">
                                    <br/>${ dict_data['Emisor']['DomicilioFiscal']['@calle'] or ''|entity}
                                    ${ dict_data['Emisor']['DomicilioFiscal']['@noExterior'] or ''|entity}
                                    ${ dict_data['Emisor']['DomicilioFiscal']['@noInterior'] or ''|entity}</br>
                                    ${ dict_data['Emisor']['DomicilioFiscal']['@colonia'] or ''|entity}
                                    ${ dict_data['Emisor']['DomicilioFiscal']['@codigoPostal'] or ''|entity}
                                    <br/>${ _("Localidad:")} ${ dict_data['Emisor']['DomicilioFiscal']['@localidad'] or ''|entity}                                    
                                    <br/>${ dict_data['Emisor']['DomicilioFiscal']['@municipio'] or ''|entity}                                    
                                    , ${ dict_data['Emisor']['DomicilioFiscal']['@estado'] or ''|entity}                                    
                                    , ${ dict_data['Emisor']['DomicilioFiscal']['@pais'] or ''|entity}
                                    <br/><b>${_("RFC:")} ${dict_data['Emisor']['@rfc'] or ''|entity}</b>
                                    <br/>${ dict_data['Emisor']['RegimenFiscal']['@Regimen'] or ''|entity }
                                 </div>
                            </td>
                            <td class="td_data_exp">
                                <div class="fiscal_address">
                                    <br/>Expedido en:
                                        ${ dict_data['Emisor']['@nombre'] or ''|entity}
                                        <br/>${ dict_data['Emisor']['ExpedidoEn']['@calle'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@noExterior'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@noInterior'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@colonia'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@codigoPostal'] or ''|entity}
                                        <br/>Localidad: ${ dict_data['Emisor']['ExpedidoEn']['@localidad'] or ''|entity}
                                        <br/>${ dict_data['Emisor']['ExpedidoEn']['@municipio'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@estado'] or ''|entity}
                                        ${ dict_data['Emisor']['ExpedidoEn']['@pais'] or ''|entity}
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
                            <td width="64%" class="cliente">${ dict_data['Receptor']['@nombre'] or ''|entity}</td>
                            <td class="cliente"><b>R. F. C.:</b></td>
                            <td width="16%" class="cliente"><b>${ dict_data['Receptor']['@rfc'] or ''|entity}</b></td>
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="7%" class="cliente"><b>Calle:</b></td>
                            <td class="cliente">${ dict_data['Receptor']['Domicilio']['@calle'] or ''|entity}</td>
                            <td width="9%" class="cliente"><b>No. Ext:</b></td>
                            <td width="9%" class="cliente">${ dict_data['Receptor']['Domicilio']['@noExterior'] or ''|entity}</td>
                            <td width="9%" class="cliente"><b>No. Int:</b></td>
                            <td width="9%" class="cliente">${ dict_data['Receptor']['Domicilio']['@noInterior'] or ''|entity}</td>
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="10%" class="cliente"><b>Colonia:</b></td>
                            <td class="cliente">${ dict_data['Receptor']['Domicilio']['@colonia'] or ''|entity}</td>
                            <td width="7%" class="cliente"><b>C.P.:</b></td>
                            <td class="cliente">${ dict_data['Receptor']['Domicilio']['@codigoPostal'] or ''|entity}</td>
                            <td width="12%" class="cliente"><b>Localidad:</b></td>
                            <td class="cliente">${ dict_data['Receptor']['Domicilio']['@localidad'] or ''|entity}</td>
                        </tr>
                    </table>
                    <table class="basic_table" style="border-bottom:1px solid #002966;">
                        <tr>
                            <td width="9%" class="cliente"><b>Lugar:</b></td>
                            <td class="cliente">
                                ${ dict_data['Receptor']['Domicilio']['@municipio'] or ''|entity},
                                ${ dict_data['Receptor']['Domicilio']['@estado'] or ''|entity},
                                ${ dict_data['Receptor']['Domicilio']['@pais'] or ''|entity}
                            </td>
                        </tr>
                    </table>
                </td>
                <td width="1%"></td>
                <td width="19%" align="center">
                    ${ dict_data['@LugarExpedicion'] or ''|entity}
                    <% from datetime import datetime %>
                    <br/>${_("a")} ${datetime.strptime(dict_data['@fecha'].encode('ascii','replace'), '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y %H:%M:%S') or ''|entity}
                    <br/>${_("Serie:")} ${ dict_data['@serie'] or _("Sin serie")|entity}
                </td>
            </tr>
        </table>
        <br/>   
        <table class="basic_table" style="color:#121212">
            <tr class="firstrow">
                <th width="10%">${_("Cant.")}</th>
                <th width="10%">${_("Unidad")}</th>
                <th>${_("Descripci&oacute;n")}</th>
                <th width="9%" >${_("P.Unitario")}</th>
                <th width="15%">${_("Importe")}</th>
            </tr>
            <%row_count = 1%>
            %if not isinstance(dict_data['Conceptos']['Concepto'], list):
                <% dict_lines =  [dict_data['Conceptos']['Concepto']]%>
            %else:
                <% dict_lines =  dict_data['Conceptos']['Concepto']%>
            %endif
            %for dict in range(0,len(dict_lines)):
                %if (row_count%2==0):
                    <tr  class="nonrow">
                %else:
                    <tr>
                %endif
                    <td width="10%" class="number_td"><% qty = dict_lines[dict]['@cantidad'] %>${ qty or '0.0'}</td>
                    <td width="10%" class="basic_td"><% uni = dict_lines[dict]['@unidad'] %>${ uni or '0.0'}</td>
                    <td class="basic_td"><% desc = dict_lines[dict]['@descripcion'] %>${ desc or '0.0'}</td>
                    <td width="9%" class="number_td"><% vuni = dict_lines[dict]['@valorUnitario'] %>${ vuni or '0.0'}</td>
                    <td width="15%" class="number_td"><% imp = dict_lines[dict]['@importe'] %>${ imp or '0.0'}</td>
                    </tr>
                <%row_count+=1%>
            %endfor
        </table>
        <table align="right" width="30%" style="border-collapse:collapse">
            <tr>
                <td class="total_td">${_("Sub Total:")}</td>
                <td align="right" class="total_td">$ ${ dict_data['@subTotal'] or ''|entity}</td>
            </tr>
            %if not isinstance(dict_data['Impuestos']['Traslados']['Traslado'], list):
                <% dict_imp =  [dict_data['Impuestos']['Traslados']['Traslado']]%>
            %else:
                <% dict_imp =  dict_data['Impuestos']['Traslados']['Traslado']%>
            %endif
            %for imp in range(0,len(dict_imp)):
            <tr>
                <td class="tax_td">
                    <% imp_name = dict_imp[imp]['@impuesto'] %>
                    <% tasa = dict_imp[imp]['@tasa'] %>
                    <% text = imp_name+' ('+tasa+') %' %>${ text or '0.0'}
                </td>
                <td class="tax_td" align="right">
                    <% importe = dict_imp[imp]['@importe'] %>${importe or ''|entity}
                </td>
            </tr>
            %endfor       
            <tr align="left">
                <td class="total_td"><b>${_("Total:")}</b></td>
                <td class="total_td" align="right"><b>$ ${ dict_data['@total'] or ''|entity}</b></td>
            </tr>
        </table>
        <br clear="all" />
        <table class="basic_table">
            <tr>
                <td class="tax_td">
                    ${_("IMPORTE CON LETRA:")}
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    <% amount_in_text = amount_to_text(float(dict_data['@total'].encode('ascii','replace')),dict_data['@Moneda']) %>
                    <i>${ amount_in_text or ''|entity}</i>
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    ${_('PAGO EN UNA SOLA EXHIBICI&Oacute;N - EFECTOS FISCALES AL PAGO')}
                </td>
            </tr>            
        </table>
        <br clear="all"/>      
        <!-- Inicio Nodo Nómina -->
        %if dict_data['Complemento'].has_key('Nomina'):
            <table width="100%" class="regular_table">
                <tr>
                    <td width="50%" style="text-align:center; border:1.5px solid grey;">
                        <b>${_('DATOS DEL EMPLEADO')}</b>
                    </td>
                    <td width="50%" style="text-align:center; border:1.5px solid grey;">
                        <b>${_('INFORMACIÓN LABORAL')}</b>
                    </td>
                </tr>
                <tr>
                    <td width="50%" style="border:1.5px solid grey;">
                        <table class="regular_table">
                            <tr>                                
                                <td width="25%">
                                    ${_('No. Empleado')}</br>
                                    ${_('Reg. Patronal')}</br>
                                    ${_('Puesto')}</br>
                                    ${_('CURP')}</br>
                                    ${_('Riesgo de puesto')}</br>
                                    ${_('Departamento')}</br>
                                    ${_('Núm. seguridad social')}</br>
                                </td>
                                <td width="25%">
                                    ${ dict_data['Complemento']['Nomina']['@NumEmpleado'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@RegistroPatronal'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@Puesto'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@CURP'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@RiesgoPuesto'] or ''|entity }</br>                                   
                                    ${ dict_data['Complemento']['Nomina']['@Departamento'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@NumSeguridadSocial'] or ''|entity }</br>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td width="50%" style="border:1.5px solid grey;">
                        <table class="regular_table">
                            <tr>
                                <td width="25%">
                                    ${_('Contrato')}</br>
                                    ${_('Días Pagados')}</br>
                                    ${_('Rel. Laboral')}</br>
                                    ${_('Salario diario')}</br>                                    
                                    ${_('Jornada')}</br>
                                    ${_('Antiguedad')}</br>
                                    ${_('Salario base')}</br>
                                    ${_('Periodo')}</br>                                 
                                </td>
                                <td width="25%">
                                    ${ dict_data['Complemento']['Nomina']['@TipoContrato'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@NumDiasPagados'] or ''|entity }</br>
                                    ${datetime.strptime(dict_data['Complemento']['Nomina']['@FechaInicioRelLaboral'].encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</br>
                                    ${ dict_data['Complemento']['Nomina']['@SalarioDiarioIntegrado'] or ''|entity }</br>                                
                                    ${ dict_data['Complemento']['Nomina']['@TipoJornada'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@Antiguedad'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@SalarioBaseCotApor'] or ''|entity }</br>
                                    ${ dict_data['Complemento']['Nomina']['@PeriodicidadPago'] or ''|entity }</br>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            <br/>
            <table width="100%">
                <tr>
                    <table width="100%" class="regular_table">
                        <tr>
                            <td style="text-align:center; border:1.5px solid grey;">
                                <b>${_('PAGO')}</b>
                            </td>
                        </tr>
                    </table>
                </tr>
                <tr>
                    <table width="100%" class="regular_table" style="border:1.5px solid grey;">
                        <tr>                          
                            <td>${_('Fecha Pago')}</td><td>${datetime.strptime(dict_data['Complemento']['Nomina']['@FechaPago'].encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                            <td>${_('Fecha Inicio')}</td><td>${datetime.strptime(dict_data['Complemento']['Nomina']['@FechaInicialPago'].encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                            <td>${_('Fecha Fin')}</td><td>${datetime.strptime(dict_data['Complemento']['Nomina']['@FechaFinalPago'].encode('ascii','replace'), '%Y-%m-%d').strftime('%d/%m/%Y') or ''|entity}</td>
                        </tr>
                        <tr>
                            <td>${_('CLABE')}</td><td>${ dict_data['Complemento']['Nomina']['@CLABE'] or ''|entity }</td>
                            <td>${_('Método de pago')}</td><td>${ dict_data['@metodoDePago'] or ''|entity }</td>
                            <td>${_('Banco')}</td><td>${ dict_data['Complemento']['Nomina']['@Banco'] or ''|entity } </td>
                        </tr>
                    </table>
                </tr>
            </table>
            <br/>   
            <table width="100%" class="regular_table">
                <tr>
                    <td width="50%" valign="top">
                        <table class="regular_table">
                            <tr style="border:1.5px solid grey;">
                                <td width="10%" colspan="5"><b>${_('PERCEPCIONES')}</b></td>
                            </tr>
                            <tr style="border:1.5px solid grey;">
                                <td width="5%">${_('Tipo')}</td>
                                <td width="10%">${_('Clave')}</td>
                                <td>${_('Concepto')}</td>
                                <td width="11%" >${_('Importe Gravado')}</td>
                                <td width="11%" >${_('Importe Exento')}</td>
                            </tr>
                            %if not isinstance(dict_data['Complemento']['Nomina']['Percepciones']['Percepcion'], list):
                                <% dict_perc =  [dict_data['Complemento']['Nomina']['Percepciones']['Percepcion']] %>
                            %else:
                                <% dict_perc =  dict_data['Complemento']['Nomina']['Percepciones']['Percepcion'] %>
                            %endif
                            %for dict in range(0,len(dict_perc)):
                                <tr style="border:1.5px solid grey;">
                                    <td width="5%" class="basic_td"><% t_perc = dict_perc[dict]['@TipoPercepcion'] %>${ t_perc or ''}</td>
                                    <td width="10%" class="basic_td"><% clave = dict_perc[dict]['@Clave'] %>${ clave or ''}</td>
                                    <td class="basic_td"><% concep = dict_perc[dict]['@Concepto'] %>${ concep or ''}</td>
                                    <td width="11%" class="number_td"><% i_grava = dict_perc[dict]['@ImporteGravado'] %>$ ${ i_grava or '0.0'}</td>
                                    <td width="15%" class="number_td"><% i_exen = dict_perc[dict]['@ImporteExento'] %>$ ${ i_exen or '0.0'}</td>
                                </tr>
                             %endfor
                             <tr style="border:1.5px solid grey;">
                                <td class="basic_td" colspan="3"><b>${_('Total Percepciones')}</b></td>
                                <td width="9%" class="number_td">$ ${ dict_data['Complemento']['Nomina']['Percepciones']['@TotalGravado'] or '0.0'|entity}</td>
                                <td width="15%" class="number_td">$ ${ dict_data['Complemento']['Nomina']['Percepciones']['@TotalExento'] or '0.0'|entity}</td>
                            </tr>
                        </table>
                    </td>
                    <td width="50%" valign="top">
                        <table class="regular_table">
                            <tr style="border:1.5px solid grey;">
                                <td width="10%" colspan="5"><b>${_('DEDUCCIONES')}</b></td>
                            </tr>
                            <tr style="border:1.5px solid grey;">
                                <td width="5%">${_('Tipo')}</td>
                                <td width="10%">${_('Clave')}</td>
                                <td>${_('Concepto')}</td>
                                <td width="11%" >${_('Importe Gravado')}</td>
                                <td width="11%" >${_('Importe Exento')}</td>
                            </tr>
                            %if not isinstance(dict_data['Complemento']['Nomina']['Deducciones']['Deduccion'], list):
                                <% dict_deduc =  [dict_data['Complemento']['Nomina']['Deducciones']['Deduccion']] %>
                            %else:
                                <% dict_deduc =  dict_data['Complemento']['Nomina']['Deducciones']['Deduccion'] %>
                            %endif
                            %for dict in range(0,len(dict_deduc)):
                                <tr style="border:1.5px solid grey;">
                                    <td width="5%" class="basic_td"><% t_deduc = dict_deduc[dict]['@TipoDeduccion'] %>${ t_deduc or ''}</td>
                                    <td width="10%" class="basic_td"><% clave = dict_deduc[dict]['@Clave'] %>${ clave or ''}</td>
                                    <td class="basic_td"><% concep = dict_deduc[dict]['@Concepto'] %>${ concep or ''}</td>
                                    <td width="11%" class="number_td"><% i_grava = dict_deduc[dict]['@ImporteGravado'] %>$ ${ i_grava or '0.0'}</td>
                                    <td width="15%" class="number_td"><% i_exen = dict_deduc[dict]['@ImporteExento'] %>$ ${ i_exen or '0.0'}</td>
                                </tr>
                            %endfor
                            <tr style="border:1.5px solid grey;">
                                <td class="basic_td" colspan="3"><b>${_('Total Deducciones')}</b></td>
                                <td width="9%" class="number_td">$ ${ dict_data['Complemento']['Nomina']['Deducciones']['@TotalGravado']or '0.0'|entity}</td>
                                <td width="15%" class="number_td">$ ${ dict_data['Complemento']['Nomina']['Deducciones']['@TotalExento']or '0.0'|entity}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                <td width="50%" valign="top">
                    <table class="regular_table">
                        <tr style="border:1.5px solid grey;">
                            <td width="10%" colspan="4"><b>${_('HORAS EXTRAS')}</b></td>
                        </tr>
                        <tr style="border:1.5px solid grey;">
                            <td width="10%">${_('Dias')}</td>
                            <td width="10%">${_('Tipo')}</td>
                            <td width="9%" >${_('Cant. de hrs')}</td>
                            <td width="9%" >${_('Importe')}</td>
                        </tr>
                        %if not isinstance(dict_data['Complemento']['Nomina']['HorasExtras']['HorasExtra'], list):
                            <% dict_he =  [dict_data['Complemento']['Nomina']['HorasExtras']['HorasExtra']] %>
                        %else:
                            <% dict_he =  dict_data['Complemento']['Nomina']['HorasExtras']['HorasExtra'] %>
                        %endif
                        %for dict in range(0,len(dict_he)):
                            <tr style="border:1.5px solid grey;">
                                <td width="10%" class="basic_td"><% dias = dict_he[dict]['@Dias'] %>${ dias or '' | entity}</td>
                                <td width="10%" class="basic_td"><% tipo = dict_he[dict]['@TipoHoras'] %>${ tipo or '' | entity}</td>
                                <td width="9%" class="basic_td"><% hrs = dict_he[dict]['@HorasExtra'] %>${ hrs or '' | entity}</td>
                                <td width="10%" class="number_td"><% imp = dict_he[dict]['@ImportePagado'] %>${ imp or '0.0' | entity}</td>
                            </tr>
                        %endfor
                    </table>
                </td>
                <td width="50%" valign="top">
                    <table class="regular_table">
                        <tr style="border:1.5px solid grey;">
                            <td width="10%" colspan="3"><b>${_('INCAPACIDAD')}</b></td>
                        </tr>
                        <tr style="border:1.5px solid grey;">
                            <td width="10%">${_('Dias')}</td>
                            <td width="10%">${_('Tipo')}</td>
                            <td width="9%">${_('Importe')}</td>
                        </tr>
                        %if not isinstance(dict_data['Complemento']['Nomina']['Incapacidades']['Incapacidad'], list):
                            <% dict_inc =  [dict_data['Complemento']['Nomina']['Incapacidades']['Incapacidad']] %>
                        %else:
                            <% dict_inc =  dict_data['Complemento']['Nomina']['Incapacidades']['Incapacidad'] %>
                        %endif
                        %for dict in range(0,len(dict_inc)):
                            <tr style="border:1.5px solid grey;">
                                <td width="10%" class="basic_td"><% dias = dict_inc[dict]['@DiasIncapacidad'] %>${ dias or '' | entity}</td>
                                <td width="10%" class="basic_td"><% tipo = dict_inc[dict]['@TipoIncapacidad'] %>${ tipo or '' | entity}</td>
                                <td width="9%" class="number_td"><% desc = dict_inc[dict]['@Descuento'] %>${ desc or '0.0' | entity}</td>
                            </tr>
                        %endfor
                    </table>
                </td>
            </tr>
            </table>
        %endif
        <!-- Fin Nodo Nómina -->
        <br clear="all"/>
        <font class="font">“Este documento es una representación impresa de un CFDI”
        <br/>CFDI, Comprobante Fiscal Digital por Internet</font>
        <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                <tr>
                    <th width="33%"> ${_('Certificado del SAT')}</th>
                    <th> ${_('Fecha de Timbrado')}</th>
                    <th width="33%"> ${_('Folio Fiscal')}</th>
                </tr>
                <tr>
                    <td width="33%" class="center_td"> ${ dict_data['Complemento']['TimbreFiscalDigital']['@noCertificadoSAT'] or 'No identificado'|entity }</td>
                    <td width="34%" class="center_td"> ${ datetime.strptime(dict_data['Complemento']['TimbreFiscalDigital']['@FechaTimbrado'].encode('ascii','replace'), '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y %H:%M:%S') or 'No identificado'|entity }</td>
                    <td width="33%" class="center_td"> ${ dict_data['Complemento']['TimbreFiscalDigital']['@UUID'] or 'No identificado'|entity }</td>
                </tr>
        </table>
        <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                <tr>
                    <th width="33%">${_('Certificado del emisor')}</th>
                    <th width="34%">${_('M&eacute;todo de Pago')}</th>
                    <th width="33%">${_('&Uacute;ltimos 4 d&iacute;gitos de la cuenta bancaria')}</th>
                </tr>
                <tr>
                    <td class="center_td">${ dict_data['@noCertificado'] or 'No identificado'|entity }</td>
                    <td class="center_td">${ dict_data['@metodoDePago'] or 'No identificado'|entity }</td>
                    <td class="center_td">${ dict_data['@NumCtaPago'] or 'No identificado'|entity }</td>
                </tr>
        </table>
        <div style="page-break-inside:avoid; border:1.5px solid grey;">
            <table width="100%" class="datos_fiscales">
                <tr>
                    <td align="left">
                        ${helper.embed_image('jpeg',str(o.company_id.cif_file), 140, 220)}
                    </td>
                    <td valign="top" align="left">
                        <p class="cadena_with_cbb_cfd">
                        <b>${_('Sello Digital Emisor:')} </b><br/>
                        ${ dict_data['@sello'] or ''|entity}<br/>
                        <b>${_('Sello Digital SAT:')} </b><br/>
                        ${ dict_data['Complemento']['TimbreFiscalDigital']['@selloSAT'] or ''|entity}<br/>
                        <b>${_('Cadena original:')} </b><br/>
                        ${o.cfdi_cadena_original or ''|entity}</br>
                        <b>${_('Enlace al certificado: ')}</b></br>
                        ${'' or ''|entity}</p>
                    </td>
                    <td align="right">
                        <% img = create_qrcode(dict_data['Emisor']['@rfc'], dict_data['Receptor']['@rfc'], float(dict_data['@total'].encode('ascii','replace')), dict_data['Complemento']['TimbreFiscalDigital']['@UUID']) %>
                        ${helper.embed_image('jpeg',str(img),180, 180)}
                    </td>
                </tr>
            </table>
        </div>
        <p style="page-break-after:always"></p>
    %endfor
</body>
</html>
