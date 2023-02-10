import logging
import re
from datetime import datetime

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _name = "pull.request"

    title = fields.Char(index=True)
    repo_id = fields.Many2one("module.repo", string="Host Repository")
    date_open = fields.Datetime(string="Opening Date")
    date_updated = fields.Datetime(string="Date of Last Update")
    date_closed = fields.Datetime(string="Date of close")
    module_ids = fields.One2many(
        "module.information", "module_id", string="Modules Concerned"
    )
    version_id = fields.Many2one("odoo.version")
    reviewer_ids = fields.Many2many("res.users")
    # TODO reviewer_count = fields.Integer(compute="count_")
    state = fields.Char()
    # url = fields.Char(related='repo_id.url', store=True)
    url = fields.Char()

    def get_pr_states(self):
        # called by cron

        # create 1 job for each repo
        repos = self.env["module.repo"].search([])
        for repo in repos:
            if repo.modules_ids:
                url = f"https://api.github.com/repos/{repo.organization}/{repo.name}/pulls"
                self.with_delay(
                    max_retries=2, description=f"import PR infos for repo {repo.name}"
                ).import_pr(url, repo)

    def get_module_from_pr(self, url, modules):
        # TO change, load one time ?
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        response = requests.get(url, headers={"authorization": f"Bearer {git_token}"})
        matchs = re.findall(r"\+{3,5} b.*", response.text)
        module_ids = []
        for line in matchs:
            # regex sur le path, get first /module/
            module_name = re.search(r"(?<=/)(\w*)(?=/)", line)
            # _logger.info("MODULE NAME: %s", module_name.group(0))
            if not module_name:
                continue
            module_name = module_name.group(0)
            module_id = modules.get(module_name)
            if module_id and module_id not in module_ids:
                module_ids.append(module_id)
        _logger.info("MODULE TROUVES: %s", module_ids)
        return module_ids

    def import_pr(self, url, repo):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        modules = {
            m.technical_name: m.id for m in self.env["module.information"].search([])
        }
        response = requests.get(url, headers={"authorization": f"Bearer {git_token}"})
        prs = response.json()
        odoo_version_dct = {
            v.version: v.id for v in self.env["odoo.version"].search([])
        }
        for pr in prs:
            if not odoo_version_dct.get(pr["base"]["ref"][:4], False):
                continue
            vals = {
                "title": pr["title"],
                "repo_id": repo[0].id,
                "date_open": datetime.strptime(
                    pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "module_ids": [
                    (6, 0, self.get_module_from_pr(pr["diff_url"], modules))
                ],
                "version_id": odoo_version_dct.get(pr["base"]["ref"][:4], ""),
                "state": pr["state"],
                "url": pr["html_url"],
            }

            if pr.get("updated_at", False):
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
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            pr_obj = self.search([("title", "=", pr["title"])])
            _logger.info(
                "\n >>> MODULE AVANT CREATE: %s, obj: %s\n vals: %s",
                pr["title"],
                pr_obj,
                vals,
            )

            if pr_obj:
                pr_obj.ensure_one()
                pr_obj.write(vals)
                _logger.info("WRITE vals %s", vals)
            else:
                pr_obj.create(vals)
                _logger.info("CREATE vals %s", vals)
