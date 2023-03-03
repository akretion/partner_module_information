import logging
from datetime import datetime

import requests

from odoo import fields, models

# from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class ModuleRepo(models.Model):
    _inherit = "module.repo"

    # updated_at = fields.Datetime(string="Last Update")
    date_last_updated = fields.Datetime(
        string="Last Update date", default="2023-01-01"
    )  # default=date_utils.json_default

    def cron_import_pr(self):
        repos = self.search([])
        for repo in repos:
            repo.with_delay(
                max_retries=2,
                description="import PR infos for repo: "
                f"{repo.organization}/{repo.name}",
            ).import_pr()

    def import_pr(self):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        odoo_version_dct = {
            v.version: v.id for v in self.env["odoo.version"].search([])
        }
        for repo in self:
            modules = {m.technical_name: m.id for m in repo.module_ids}
            last_updated = repo.date_last_updated.strftime("%Y-%m-%d")
            url = (
                "https://api.github.com/search/issues?q=repo:"
                f"{repo.organization}/{repo.name}+is:pr+updated:%3E="
                f"{last_updated}&per_page=100"
            )
            response = requests.get(
                url, headers={"authorization": f"Bearer {git_token}"}
            )
            # _logger.info(">>>>> PULL url: %s \n res = %s", url, response.json())

            prs = response.json()["items"]
            if not prs:
                # no PR to update
                continue
            # _logger.info(">>>>> PULL TOTAL COUNT = %s", response.json()["total_count"])

            max_updated = prs[0]["updated_at"]
            for pr in prs:
                response = requests.get(
                    pr["pull_request"]["url"],
                    headers={"authorization": f"Bearer {git_token}"},
                )
                _logger.info("\n >>>>> REST GET PULL duration: %s", response.elapsed)
                pull = response.json()
                max_updated = max(pr["updated_at"], max_updated)
                if not odoo_version_dct.get(pull["base"]["ref"][:4], False):
                    continue
                self.env["pull.request"].create_or_update_pr(
                    pull, repo, modules, odoo_version_dct
                )
            repo.date_last_updated = datetime.strptime(
                max_updated, "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%d")

    def action_view_module(self):
        self.ensure_one()
        modules = self.mapped("module_ids")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "module_info_partner.module_information_action"
        )
        if len(modules) > 0:
            action["domain"] = [("id", "in", modules.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def get_pr_state(self):
        self.import_pr()
        return True
