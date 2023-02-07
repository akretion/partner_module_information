import logging
from datetime import datetime

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _name = "pull.request"

    title = fields.Char(index=True)
    repo_id = fields.Many2one("host.repository", string="Host Repository")
    date_open = fields.Datetime(string="Opening Date")
    date_updated = fields.Datetime(string="Date of Last Update")
    date_closed = fields.Datetime(string="Date of close")
    module_ids = fields.One2many(
        "module.information", "module_id", string="Modules Concerned"
    )
    version_id = fields.Many2one("odoo.version")
    reviewer_one_id = fields.Many2one("res_partner")
    reviewer_two_id = fields.Many2one("res_partner")
    state = fields.Char()
    # url = fields.Char(related='repo_id.url', store=True)
    url = fields.Char()

    def get_pr_states(self):
        # called by cron

        # create 1 job for each repo
        repos = self.env["host.repository"].search([])
        for repo in repos:
            if repo.modules_ids:
                url = f"https://api.github.com/repos/{repo.organization}/{repo.name}/pulls"
                self.with_delay(
                    max_retries=2, description=f"import PR infos for repo {repo.name}"
                ).import_pr(url, repo)
                # break  # for test

    def import_pr(self, url, repo):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        response = requests.get(url, headers={"authorization": f"Bearer {git_token}"})
        prs = response.json()
        odoo_version_dct = {
            v.version: v.id for v in self.env["odoo.version"].search([])
        }
        for pr in prs:
            vals = {
                "title": pr["title"],
                "repo_id": repo[0].id,
                "date_open": datetime.strptime(
                    pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d %H:%M:%S"),
                # date_closed
                # 'module_ids': # voir en appellant l'url du diff:
                # "https://github.com/akretion/ak-odoo-incubator/pull/257.diff"
                "version_id": odoo_version_dct.get(
                    pr["base"]["ref"][:4],
                    odoo_version_dct["Unknown version, please update odoo.version"],
                ),
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
            if pr_obj:
                pr_obj.ensure_one()
                pr_obj.write(vals)
            else:
                pr_obj.create(vals)
