<html>

	<head>
		<style type="text/css">${css}</style>
	</head>

	<body>
	
		% for user.story in objects:
			
			<table width="100%">
				<tr>
					<th class="panel_bg_color_title">${_("USER STORY NAME")}</th>
				</tr>
				<tr height="10"></tr>
				<tr>
					<td class="td_center">${user and user.story and user.story.name}</td>
				</tr>	
				<tr height="20"></tr>								
			</table>
			<table width="100%">
				<tr>
					<th class="th_center panel_bg_color_title">${_("PROJECT NAME:")}</th>
					<td class="panel_bg_color">${user and user.story and user.story.project_id and user.story.project_id.name}</td>
				</tr>
				<tr>
					<th class="th_center panel_bg_color_title">${_("OWNER:")}</th>
					<td class="panel_bg_color">${user and user.story and user.story.owner_id and user.story.owner_id.name}</td>
				</tr>
				<tr>
					<th class="th_center panel_bg_color_title">${_("PLANNED HOURS:")}</th>
					<td class="panel_bg_color">${user and user.story and user.story.planned_hours}</td>
				</tr>
				<tr height="20"></tr>				
			</table>
			<table width="100%">
				<tr>
					<th class="panel_bg_color_title">${_("DESCRIPTION")}</th>
				</tr>
				<% import html2text %>
				<% text = html2text.html2text(user.story.description or '') %>
				<tr>
					<td class="pre_description">${text or '' | entity}</td>
				</tr>
				<tr height="30"></tr>
			</table>
			<table width="100%">
				<tr>
					<th class="panel_bg_color_title">${_("ACCEPTABILITY CRITERIA")}</th>
				</tr>				
			</table>
			<table width="100%">
				<tr>
					<th class="th_center panel_bg_color_title">>${_("Name")}</th>
					<th class="th_center panel_bg_color_title">>${_("Scenario")}</th>
				</tr>
				
				% for criteria in (user and user.story and user.story.accep_crit_ids):
					<tr>
						<td class="panel_bg_color">${criteria.name}</td>
						<td class="panel_bg_color">${criteria.scenario}</td>
					</tr>
				% endfor
				
			</table>
									
		% endfor
	
	</body>

</html>
