<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        <table>
            <tr>
                <td>
                    <div>
                        ${_("Invoice Demo Report")}
                    </div>
                </td>
            </tr>
        </table>
    %endfor
</body>
</html>
