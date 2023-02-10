from odoo import api, fields, models


class ModulePartner(models.Model):
    _name = "module.partner"
    _description = "Modules used by partner"

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, string="Partner"
    )
    version_id = fields.Many2one(
        "odoo.version", string="Version", required=True, index=True
    )
    module_id = fields.Many2one(
        "module.information", required=True, index=True, string="Module"
    )

    @api.model
    def _prepare_module_info_vals(self, module_info):
        return {
            "technical_name": module_info.get("name"),
            "name": module_info.get("shortdesc"),
            "description_html": module_info.get("description"),
            "authors": module_info.get("author"),
            # ajouter le champs partner_id si iscustom
        }

    @api.model
    def _prepare_partner_module_vals(self, partner, version, module, module_info):
        return {
            "partner_id": partner.id,
            "version_id": version.id,
            "module_id": module.id,
        }

    @api.model
    def update_or_create(self, partner, version_num, module_info):
        tech_name = module_info.get("name")
        # check if module already exists
        module_info_obj = self.env["module.information"]
        module = module_info_obj.search(
            [
                ("technical_name", "=", tech_name),
                "|",
                ("partner_id", "=", False),
                ("partner_id", "=", partner.id),
            ]
        )
        if not module:
            module = module_info_obj.create(self._prepare_module_info_vals(module_info))
        version = self.env["odoo.version"].search([("version", "=", version_num)])
        partner_module_vals = self._prepare_partner_module_vals(
            partner, version, module, module_info
        )

        partner_module = self.search(
            [
                ("partner_id", "=", partner.id),
                ("module_id", "=", module.id),
                ("version_id", "=", version.id),
            ]
        )
        if partner_module:
            partner_module.write(partner_module_vals)
        else:
            partner_module = self.create(partner_module_vals)

        # if module is not listed in module.version, we create it.
        # if we use the module to synchronize module_information from
        # github_connector_odoo, we should rarely create any module.version
        # from here except for custom modules.

        # we can't know if it is merged or in PR, let's consider it in PR (pending)
        # it will be updated by synchro with github_connector_odoo (if
        # used) or manually
        module_version = self.env["module.version"].search(
            [("module_id", "=", module.id), ("version_id", "=", version.id)]
        )
        if not module_version:
            self.env["module.version"].create(
                {"module_id": module.id, "version_id": version.id, "state": "pending"}
            )
        return partner_module
