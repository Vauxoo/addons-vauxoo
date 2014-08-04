<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang(user.lang) %>
    %for o in objects:
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
            <% cur_group = get_aged_lines( objects, inv_type='out_invoice') %>
            %for table in cur_group:
            <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
                <tr>
                    <th width="12%" class="ITEMSTITLELEFT">${_('TIN') |entity}</th>
                    <th width="18%" class="ITEMSTITLELEFT">${_('PARTNER') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('NOT DUE') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">01-30 ${_('DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">31-60 ${_('DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">61-90 ${_('DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">91-120 ${_('DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">+ 120 ${_('DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('TOT./AR')}${"(" + table[0].get('cur_brw', False).name+ ")" |entity}</th>
                </tr>
            </table>
            </br>
            %endfor
</br>
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>

    %endfor

</body>
</html>
