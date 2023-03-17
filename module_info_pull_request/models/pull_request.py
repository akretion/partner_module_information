import logging
import re
from datetime import datetime

import requests

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _name = "pull.request"

    def _domain_project_id(self):
        domain = [("allow_timesheets", "=", True)]
        if not self.user_has_groups("hr_timesheet.group_timesheet_manager"):
            return expression.AND(
                [
                    domain,
                    [
                        "|",
                        ("privacy_visibility", "!=", "followers"),
                        ("allowed_internal_user_ids", "in", self.env.user.ids),
                    ],
                ]
            )
        return domain

    title = fields.Char(index=True, readonly=True)
    repo_id = fields.Many2one(
        "module.repo", string="Host Repository", index=True, readonly=True
    )
    date_open = fields.Datetime(string="Opening Date", readonly=True)
    date_updated = fields.Datetime(string="Date of Last Update", readonly=True)
    date_closed = fields.Datetime(string="Date of close", readonly=True)
    module_ids = fields.Many2many(
        "module.information", string="Related Modules", readonly=True
    )
    version_id = fields.Many2one("odoo.version", readonly=True, index=True)
    reviewer_ids = fields.Many2many("res.users")
    reviewer_count = fields.Integer(compute="_compute_reviewer", readonly=True)
    state = fields.Char(index=True, readonly=True)
    url = fields.Char(readonly=True)
    number = fields.Integer(index=True, string="Github number", readonly=True)
    author = fields.Char(index=True, readonly=True)
    orga = fields.Char(index=True, readonly=True)
    timesheet_ids = fields.One2many("account.analytic.line", "task_id", "Timesheets")
    project_id = fields.Many2one(
        "project.project",
        "Project",
        compute="_compute_project_id",
        store=True,
        readonly=False,
        domain=_domain_project_id,
    )
    task_id = fields.Many2one(
        "project.task",
        "Task",
        compute="_compute_task_id",
        store=True,
        readonly=False,
        index=True,
        domain="["
        "('company_id', '=', company_id), "
        "('project_id.allow_timesheets', '=', True), "
        "('project_id', '=?', project_id)]",
    )

    _sql_constraints = [
        (
            "uniq_number_and_repo",
            "unique(number, repo_id)",
            "the pair pr number and repo must be unique",
        ),
    ]

    @api.depends("project_id")
    def _compute_task_id(self):
        for line in self.filtered(lambda line: not line.project_id):
            line.task_id = False

    @api.depends("reviewer_ids")
    def _compute_reviewer(self):
        for record in self:
            record.reviewer_count = len(record.reviewer_ids)

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

            # _logger.info("MAJ MODULE: %s", vals)
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
                    "author": pr["user"]["login"],
                    "orga": pr["head"]["user"]["login"],
                }
            )
            # _logger.info("CREATION MODULE: %s", vals)
            pr_obj.create(vals)

    def open_url(self):
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": self.url,
        }
