import logging
import re
from datetime import datetime

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _name = "pull.request"

    title = fields.Char(index=True)
    repo_id = fields.Many2one("module.repo", string="Host Repository", index=True)
    date_open = fields.Datetime(string="Opening Date")
    date_updated = fields.Datetime(string="Date of Last Update")
    date_closed = fields.Datetime(string="Date of close")
    module_ids = fields.Many2many("module.information", string="Related Modules")
    module_ids_nbr = fields.Integer(
        compute="_compute_module_ids_nbr", string="# of Modules"
    )
    version_id = fields.Many2one("odoo.version")
    reviewer_ids = fields.Many2many("res.users")
    reviewer_count = fields.Integer(compute="_compute_reviewer")
    state = fields.Char()
    url = fields.Char()
    number = fields.Integer(index=True, string="Github number")

    _sql_constraints = [
        (
            "uniq_number_and_repo",
            "unique(number, repo_id)",
            "the pair pr number and repo must be unique",
        ),
    ]

    @api.depends("reviewer_ids")
    def _compute_reviewer(self):
        for record in self:
            record.reviewer_count = len(record.reviewer_ids)

    @api.depends("module_ids")
    def _compute_module_ids_nbr(self):
        for record in self:
            record.module_ids_nbr = len(record.module_ids)

    def _get_module_from_pr(self, url, modules):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        response = requests.get(url, headers={"authorization": f"Bearer {git_token}"})
        matchs = re.findall(r"\+{3,5} b.*", response.text)
        module_ids = []
        for line in matchs:
            # regex get first /module/
            module_name = re.search(r"(?<=/)(\w*)(?=/)", line)
            if not module_name:
                continue
            module_name = module_name.group(0)
            module_id = modules.get(module_name)
            if module_id and module_id not in module_ids:
                module_ids.append(module_id)
        # _logger.info("MODULE TROUVÉ: %s", module_ids)
        return module_ids

    def create_or_update_pr(self, pr, repo, modules_info, odoo_version):
        vals = {}
        pr_obj = self.search(
            [("number", "=", pr["number"]), ("repo_id", "=", repo[0].id)]
        )
        if pr_obj and pr_obj.state == "open":
            # Closed PR has no update
            # PR exist in bdd and is open

            vals.update(
                {
                    "date_updated": datetime.strptime(
                        pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            if pr.get("closed_at", False):
                vals.update(
                    {
                        "date_closed": datetime.strptime(
                            pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "state": pr["state"],
                    }
                )

            _logger.info("MAJ MODULE: %s", vals)
            pr_obj.write(vals)

        elif not pr_obj and pr["state"] == "open":
            # PR not exist in bdd
            vals.update(
                {
                    "title": pr["title"],
                    "number": pr["number"],
                    "repo_id": repo[0].id,
                    "date_open": datetime.strptime(
                        pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "module_ids": [
                        (6, 0, self._get_module_from_pr(pr["diff_url"], modules_info))
                    ],
                    "version_id": odoo_version.get(pr["base"]["ref"][:4], ""),
                    "state": pr["state"],
                    "url": pr["html_url"],
                }
            )
            _logger.info("CREATION MODULE: %s", vals)
            pr_obj.create(vals)

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
