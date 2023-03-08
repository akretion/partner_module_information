import logging

import requests
import yaml

from odoo import _, api, models

_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module information synchronization")


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
        versions = self.env["odoo.version"].search([])
        for version in versions:
            data = self.get_module_info(version.version)
            for orga, repos in data.items():
                for repo, modules in repos.items():
                    for module in modules:
                        self._update_or_create_modules(version, orga, repo, module)

    @api.model
    def _update_or_create_modules(self, version, orga_name, repo_name, module):
        # odoo_version_dct = {
        #     v.version: v.id for v in self.env["odoo.version"].search([])
        # }
        repo = self._get_or_create_repo(orga_name, repo_name)
        # version_id = odoo_version_dct.get(version, "odoo_version_unknown")
        vals = {
            "repo_id": repo.id,
            "technical_name": module,
            # "description_rst":info["description"]
            # # TODO add description in odoo-module-tracker
        }
        module = self.search(
            [("technical_name", "=", module), ("partner_id", "=", False)]
        )
        if module:
            if module._should_update_module(version.version, orga_name):
                module.write(vals)
            module._add_available_version(version)
        else:
            vals.update({"available_version_ids": [(4, version.id, 0)]})
            _logger.info(">>>> CREATE MODULE : %s", vals)
            module = self.create(vals)

    @api.model
    def _get_or_create_repo(self, orga_name, repo_name):
        repo_vals = {"organization": orga_name, "name": repo_name}
        repo = self.env["module.repo"].search(
            [("name", "=", repo_name), ("organization", "=", orga_name)]
        )
        if not repo:
            repo = self.env["module.repo"].create(repo_vals)
        return repo

    @api.model
    def _add_available_version(self, version):
        # import pdb; pdb.set_trace()
        module_version = self.module_version_ids.filtered(
            lambda s: s.version_id == version
        )
        if module_version and module_version.state != "done":
            # In case that a version have been creating from a pending PR
            module_version.state = "done"
        else:
            self.env["module.version"].create(
                {
                    "module_id": self.id,
                    "version_id": version.id,
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
