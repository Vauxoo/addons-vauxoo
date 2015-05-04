<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        ${css}
        table, th, td {
            border: 1px solid grey;
            border-collapse: collapse;
            font-size: 12px;
        }
    </style>
</head>
<body style="border:0;"> 
    %for obj in objects :
     <table width="100%" style="font-size: 14px;">
        <tr>
            <th>
               <p>User</p>
            </th>
            <th>
               <p>Description</p>
            </th>
            <th>
               <p>Duration</p>
            </th>
        </tr>
        %for rec in obj.records :
        <tr>
            <td>
                <p>${rec.user_id.name}</p>
            </td>
            <td>
                <p>${rec.name}</p>
            </td>
            <td>
                <p>${rec.unit_amount}</p>
            </td>
        </tr>
        %endfor
     </table>
    <p>
    </p>
%endfor
</body>
</html>
