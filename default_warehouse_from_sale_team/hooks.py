import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    fill_user_allowed_salesteams(env)


def fill_user_allowed_salesteams(env):
    """Fill allowed sales teams in users that are already members of any team.

    Since this module implements a feature to restrict which sales teams a user may be a member of, users that already
    belong to any team are configured to be allowed for those teams, to avoid inconsistencies between allowed and
    already-configured memberships. In other words, if a user already belongs to a team, it most likely means they
    should be allowed to belong to it, so allowance is granted.
    """
    teams_per_user = env["crm.team.member"]._read_group(
        domain=[],
        groupby=["user_id"],
        aggregates=["crm_team_id:recordset"],
    )
    for user, teams in teams_per_user:
        user.sale_team_ids |= teams
    _logger.info("Field 'Allowed sales Teams' has been set to %d users.", len(teams_per_user))
