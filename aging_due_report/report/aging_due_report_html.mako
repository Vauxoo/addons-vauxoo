<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
    <table class="basic_table" width="100%">
        <tr>
            <td width="30%">
                <div  style="float:left;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, auto)}
                </div>
            </td>
       </tr>
    </table>
</br> 
    <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
        <tr>
            <th width="10%" class="ITEMSTITLELEFT">RIF</th>
            <th width="34%" class="ITEMSTITLELEFT">EMPRESA</th>
            <th width="8%" class="ITEMSTITLERIGHT">NO VENCIDO</th>
            <th width="8%" class="ITEMSTITLERIGHT">01-30 DIAS</th>
            <th width="8%" class="ITEMSTITLERIGHT">31-60 DIAS</th>
            <th width="8%" class="ITEMSTITLERIGHT">61-90 DIAS</th>
            <th width="8%" class="ITEMSTITLERIGHT">91-120 DIAS</th>
            <th width="8%" class="ITEMSTITLERIGHT">+ 120 DIAS</th>
            <th width="8%" class="ITEMSTITLERIGHT">TOT./COBRAR</th>
        </tr>
        <tr>
            <td class="ITEMSLEFT">o.get_aged_lines() o.get('type')=='partner' and o.get('rp_brw').vat and '%s-%s-%s'%(o.get('rp_brw').vat[2],o.get('rp_brw').vat[3:-1],o.get('rp_brw').vat[-1])>
                <td><para style="ITEMSLEFT">[[ o.get('type')=='partner' and o.get('rp_brw').name or o.get('type')=='total' and 'TOTAL' or o.get('type')=='provision' and removeParentNode('tr') ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('not_due'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('1to30'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('31to60'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('61to90'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('91to120'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('120+'), digits=2, grouping=True) ]]</para></td>
                <td><para style="ITEMSRIGHT">[[  formatLang(o.get('total'), digits=2, grouping=True) ]]</para></td>
            <td>${ o.vat or '' | entity}</td>
            <td class="td_center td_bold ITEMSTITLELEFT">${ o.name.upper() or '' | entity}</td>
        </tr>
    </table>
    </br>

</br>
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>

    %endfor

</body>
</html>
