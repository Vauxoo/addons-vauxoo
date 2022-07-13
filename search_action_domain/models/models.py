from odoo import api, http, models
from odoo.tools.cache import ormcache


class Base(models.AbstractModel):
    _inherit = "base"

    @ormcache("self.env.uid", "model", "action_ids", "cache_key")
    def _get_cached_action_domain_to_include(self, model, action_ids, cache_key=False):
        actions = (
            self.env["ir.actions.server"]
            .with_context(search_action_domain=False)
            .search(
                [
                    ("id", "in", action_ids.split(",")),
                    ("state", "=", "code"),
                    ("model_id.model", "=", model),
                ]
            )
        )
        domain = []
        for action in actions:
            res = action.with_context(active_model=model).run()
            res_domain = res and isinstance(res, dict) and res.get("domain")
            domain += res_domain if res_domain and isinstance(res_domain, list) else []
        return domain

    @api.model
    def _get_action_domain_to_include(self):
        ctx_dict = self.env.context.get("search_action_domain") or {}
        if not isinstance(ctx_dict, dict):
            return []
        action_ids = ctx_dict.get(self._name) or []
        if (
            not action_ids
            or not isinstance(action_ids, list)
            or not all(isinstance(aid, int) for aid in action_ids)
        ):
            return []
        return self._get_cached_action_domain_to_include(
            self._name, ",".join(map(str, action_ids)), id(http.request.httprequest)
        )

    @api.model
    def _search(self, args, *oargs, **kwargs):
        if isinstance(args, list):
            args += self._get_action_domain_to_include()
        return super(Base, self.with_context(search_action_domain=False))._search(
            args, *oargs, **kwargs
        )

    @api.model
    def _read_group_raw(self, domain, *oargs, **kwargs):
        if isinstance(domain, list):
            domain += self._get_action_domain_to_include()
        return super(
            Base, self.with_context(search_action_domain=False)
        )._read_group_raw(domain, *oargs, **kwargs)
