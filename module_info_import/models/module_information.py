# coding: utf-8

import requests
from odoo import models, api, release, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module information synchronization")


class ModuleInformation(models.Model):
    _inherit = "module.information"

    # called by cron
    @api.model
    def synchronize_module_from_github_connector_stat(self):
        # get external instance for which we want to get the data
        # must have github_connector_stat installed
        api_url = self.env["ir.config_parameter"].sudo().get_param("github.stat.url")
        if not api_url:
            return
        url = "{}/github_module_api/module/github_module_information".format(api_url)
        try:
            # FIXME Why get not working?
            res = requests.post(url)
        except Exception as e:
            _logger.error("Error when calling odoo %s", e)
            raise UserError(ERROR_MESSAGE)
        data = res.json()
        self._update_modules(data)
        if isinstance(data, dict) and data.get("code", 0) >= 400:
            _logger.error(
                "Error module sync API : %s : %s",
                data.get("name"),
                data.get("description"),
            )
            raise UserError(ERROR_MESSAGE)
        return data

    @api.model
    def _get_module_information_vals_from_github_stat(self, module_info):
        return {
            "name": module_info["name"],
            "description_rst": module_info["description_rst"],
            "description_html": module_info["description_rst_html"],
            "authors": module_info["author_ids_description"],
        }

    @api.model
    def _update_modules(self, data):
        # Since the goal is to resynchronize all modules and versions, it
        # seems appropriate to make one big search and then work with cache.
        #        existing_module = self.search([])
        #        test = dict([(x.name, x.id) for x in existing_module])
        #        existing_module_names = test.keys()
        #        for module_info in data:
        #            if module_info['technical_name'] in existing_module_names:
        #                module_id = test.get(module_info['technical_name'])
        #                self.browse(module_id).write({'name': module_info['technical_name']})
        #            else:
        #                self.create({'name': {'name': module_info['technical_name']}})
        odoo_version_dct = dict(
            [(v.version, v.id) for v in self.env["odoo.version"].search([])]
        )

        for module_info in data:
            module = self.search(
                [("technical_name", "=", module_info["technical_name"])]
            )
            vals = self._get_module_information_vals_from_github_stat(module_info)
            if module:
                module.write(vals)
                # create /update available versions of module.
                if module_info["versions"]:
                    version_modules = self.env["module.version"].search(
                        [("module_id", "=", module.id)]
                    )
                    for version in module_info["versions"]:
                        version_module = version_modules.filtered(
                            lambda m: m.version_id.version == version
                        )
                        if version_module.state == "pending":
                            version_module.state = "done"
                        elif version_module:
                            continue
                        else:
                            self.env["module.version"].create(
                                {
                                    "module_id": module.id,
                                    "version_id": odoo_version_dct[version],
                                    "state": "done",
                                }
                            )
            else:
                vals["technical_name"] = module_info["technical_name"]
                module = self.create(vals)
                # create available versions
                for version in module_info["versions"]:
                    self.env["module.version"].create(
                        {
                            "module_id": module.id,
                            "version_id": odoo_version_dct[version],
                            "state": "done",
                        }
                    )
