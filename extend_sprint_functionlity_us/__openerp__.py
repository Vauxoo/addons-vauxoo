# -*- enconding: utf-8 -*-
{
    "name": "Multiples Sprints in User Stories",
    "version": "1.1",
    "author": "Vauxoo",
    "category": "Project",
    "description": """
This module extend the functionality of the sprint in the user stories adding
the following features
- Adds a m2m fields in the user stories to allow you have an user story\
involved in multiples sprint
- Adds the sprint_id field in the acceptability criteria to define in \
what sprint was accepted
- At the moment to change the sprint in the user story the tasks related\
keep their sprint set at the moment to be created
""",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "sprint_kanban",
        "user_story",
    ],
    "data": [
        'data/sprint_data.xml',
        'view/sprint_filter_view.xml',
    ],
    "installable": True,
    "auto_install": False,
    "active": False
}
