import logging

import requests
import yaml

from odoo import _, api, models

_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module information synchronization")
VERSIONS = ["14.0", "15.0", "16.0"]


class ModuleInformation(models.Model):
    _inherit = "module.information"

    @api.model
    def get_module_info(self, version):
        url = (
            "https://raw.githubusercontent.com/akretion"
            f"/odoo-module-tracker/gh-pages/{version}.yml"
        )
        response = requests.get(url)
        return yaml.safe_load(response.text)

    # called by cron
    @api.model
    def synchronize_module(self):
        for version in VERSIONS:
            data = self.get_module_info(version)
            for orga, repos in data.items():
                for repo, modules in repos.items():
                    for module in modules:
                        self._update_or_create_modules(version, orga, repo, module)

    @api.model
    def _update_or_create_modules(self, version, orga_name, repo_name, module):
        odoo_version_dct = {
            v.version: v.id for v in self.env["odoo.version"].search([])
        }
        repo = self._get_or_create_repo(orga_name, repo_name)

        # check version
        version_id = odoo_version_dct.get(version, "odoo_version_unknown")

        vals = {
            "available_version_ids": [(4, version_id, 0)],
            "repo_id": repo.id,
            "technical_name": module,  # resultat du search
            # TODO "partner_id": get from api key
        }

        module = self.search(
            [("technical_name", "=", module), ("partner_id", "=", False)]
        )
        if module:
            if module._should_update_module(version, orga_name):
                module.write(vals)
            module._add_available_version(version)
        else:
            module = self.create(vals)

    @api.model
    def _get_or_create_repo(self, orga_name, repo_name):
        repo_vals = {"organization": orga_name, "name": repo_name}
        repo = self.env["host.repository"].search(
            [("name", "=", repo_name), ("organization", "=", orga_name)], limit=1
        )
        if repo and repo.organization != orga_name:
            self.env["host.repository"].create(repo_vals)
        elif not repo:
            repo = self.env["host.repository"].create(repo_vals)
        return repo

    @api.model
    def _add_available_version(self, version):
        if version not in self.mapped("available_version_ids.version"):
            self.env["module.version"].create(
                {
                    "module_id": self.id,
                    "version_id": self._get_version(),
                    "state": "done",
                }
            )

    @api.model
    def _should_update_module(self, version, orga):
        self.ensure_one()
        orga_priority = {"oca": 100, "akretion": 50}
        return max(
            [float(v) for v in self.mapped("available_version_ids.version")]
        ) <= float(version) and orga_priority.get(
            self.repo_id.organization, 0
        ) <= orga_priority.get(
            orga, 0
        )
