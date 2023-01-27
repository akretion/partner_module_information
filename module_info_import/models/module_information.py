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
        # make it multi version 14.0 /15.0 /16.0
        url = (
            "https://raw.githubusercontent.com/akretion"
            f"/odoo-module-tracker/gh-pages/{version}.yml"
        )
        response = requests.get(url)
        modules_list = yaml.safe_load(response.text)
        return modules_list

    # called by cron
    @api.model
    def synchronize_module(self):
        for version in VERSIONS:
            data = self.get_module_info(version)
            for orga, repos in data.items():
                for repo, modules in repos.items():
                    for module in modules:
                        self._update_modules(version, orga, repo, module)

    @api.model
    def _get_module_information_vals_from_github_stat(self, module_info):
        return {
            "name": module_info["name"],
            "description_rst": module_info["description_rst"],
            "description_html": module_info["description_rst_html"],
            "authors": module_info["author_ids_description"],
        }

    @api.model
    def _update_modules(self, version, orga, repo, module):
        odoo_version_dct = {
            v.version: v.id for v in self.env["odoo.version"].search([])
        }

        # create Host orga & repo:
        host_vals = {"organisation": orga, "name": repo}
        host_id = self.env["host.repository"].search([("name", "=", repo)], limit=1)
        if host_id and host_id.organisation != orga:
            self.env["host.repository"].create(host_vals)
        elif not host_id:
            host_id = self.env["host.repository"].create(host_vals)

        # check version
        version_id = odoo_version_dct.get(version, False)
        if not version_id:
            version_id = "odoo_version_unknown"

        vals = {
            # "name": scan manifest, module name in manifest
            # "authors":  Scan manifest
            # "module_version_ids": #to add module version (not odoo version),
            "available_version_ids": [(4, version_id, 0)],
            "host_repository_id": host_id.id,
            "technical_name": module,  # resultat du search
        }

        module = self.search([("technical_name", "=", module)])
        if module:
            vals.pop("technical_name")
            # handle case of duplicate module with different orga
            if module.host_repository_id.organisation != orga:
                prio = ["oca", "akretion"]
                if orga in prio:
                    for host in prio:
                        if host == orga:
                            vals["host_repository_id"] = host_id
                            break
                    module.write(vals)
                else:
                    if module.host_repository_id.organisation not in prio:
                        module.write(vals)
            else:
                module.write(vals)
        else:
            module = self.create(vals)
