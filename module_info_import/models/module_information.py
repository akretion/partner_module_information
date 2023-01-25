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
        url = f"https://raw.githubusercontent.com/akretion \
            /odoo-module-tracker/gh-pages/{version}.yml"
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
        # ajouter sur les repos les liste des versions

        # recoit un seul module a la fois
        # mettre a jour si la version est plus récente uniquement

        # test: faire un  mock_request sur la récupératiuon du yaml
        # et valider l'import dans module information.
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
            # "name": scan manifest
            # "authors":  Scan manifest
            "module_version_ids": [version_id],
            "host_repository_id": host_id.id,
            "technical_name": module,  # resultat du search
            # 'module_version_ids': "?"
        }

        module = self.search([("technical_name", "=", module)])
        if module:
            vals.pop("technical_name")
            module.write(vals)
        else:
            module = self.create(vals)

    #   def backup_update(self):

    #     # Since the goal is to resynchronize all modules and versions, it
    #     # seems appropriate to make one big search and then work with cache.
    #     #        existing_module = self.search([])
    #     #        test = dict([(x.name, x.id) for x in existing_module])
    #     #        existing_module_names = test.keys()
    #     #        for module_info in data:
    #     #            if module_info['technical_name'] in existing_module_names:
    #     #                module_id = test.get(module_info['technical_name'])
    #     #                self.browse(module_id).write({'name': module_info['technical_name']})
    #     #            else:
    #     #                self.create({'name': {'name': module_info['technical_name']}})
    #     odoo_version_dct = dict(
    #         [(v.version, v.id) for v in self.env["odoo.version"].search([])]
    #     )

    #     for module_info in data:
    #         module = self.search(
    #             [("technical_name", "=", module_info["technical_name"])]
    #         )
    #         vals = self._get_module_information_vals_from_github_stat(module_info)
    #         if module:
    #             module.write(vals)
    #             # create /update available versions of module.
    #             if module_info["versions"]:
    #                 version_modules = self.env["module.version"].search(
    #                     [("module_id", "=", module.id)]
    #                 )
    #                 for version in module_info["versions"]:
    #                     version_module = version_modules.filtered(
    #                         lambda m: m.version_id.version == version
    #                     )
    #                     if version_module.state == "pending":
    #                         version_module.state = "done"
    #                     elif version_module:
    #                         continue
    #                     else:
    #                         self.env["module.version"].create(
    #                             {
    #                                 "module_id": module.id,
    #                                 "version_id": odoo_version_dct[version],
    #                                 "state": "done",
    #                             }
    #                         )
    #         else:
    #             vals["technical_name"] = module_info["technical_name"]
    #             module = self.create(vals)
    #             # create available versions
    #             for version in module_info["versions"]:
    #                 self.env["module.version"].create(
    #                     {
    #                         "module_id": module.id,
    #                         "version_id": odoo_version_dct[version],
    #                         "state": "done",
    #                     }
    #                 )
