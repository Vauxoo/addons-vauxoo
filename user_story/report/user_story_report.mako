<html>
    <head>
        <style type="text/css">${css}</style>
    </head>
    <body>
        <% setLang(user.lang) %>
        % for user.story in objects:
            <table width="100%">
                <tr>
                    <th class="panel_bg_color_title">${_("User Story")}</th>
                </tr>
                <tr>
                    <td class="td_center"><h5><p class="td_margin">${user and user.story and user.story.name}</p></h5></td>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <th class="th_center panel_bg_color_title">${_("Related Project")}</th>
                    <td class="panel_bg_color">${user and user.story and user.story.project_id and user.story.project_id.name}</td>
                </tr>
                <tr>
                    <th class="th_center panel_bg_color_title">${_("Owner")}</th>
                    <td class="panel_bg_color">${user and user.story and user.story.owner_id and user.story.owner_id.name}</td>
                </tr>
                <tr>
                    <th class="th_center panel_bg_color_title">${_("Planned Hours")}</th>
                    <td class="panel_bg_color">${user and user.story and user.story.planned_hours}</td>
                </tr>
            </table>
            <p class="td_margin"></br></p>
            <table width="100%">
                <tr>
                    <th class="panel_bg_color_title">${_("Description")}</th>
                </tr>
                <tr>
                    <td class="pre_description">${parse_html_field(user.story.description)}</td>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <th class="panel_bg_color_title">${_("Acceptability Criterion")}</th>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <th width="40%" class="th_center panel_bg_color_title">${_("Name")}</th>
                    <th width="60%" class="th_center panel_bg_color_title">${_("Scenario")}</th>
                </tr>
                % for criteria in (user and user.story and user.story.accep_crit_ids):
                    <tr>
                        <td class="panel_bg_color">${criteria.name}</td>
                        <td class="panel_bg_color">${criteria.scenario}</td>
                    </tr>
                % endfor
            </table>
            <p style="page-break-before: always;"></p>
        % endfor
    </body>
</html>
