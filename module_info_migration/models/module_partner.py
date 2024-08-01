from odoo import _, api, exceptions, fields, models


class ModulePartner(models.Model):
    _inherit = "module.partner"

    migration_status = fields.Selection(
        selection=[
            ("obsolete", "Obsolete"),
            ("ongoing_pr", "Ongoing Pull Request"),
            ("done", "Done"),
        ],
        compute="_compute_migrated",
        store=True,
    )
    # task_ids = fields.Many2many('project.task', string="tasks")

    @api.depends(
        "module_id.available_version_ids",
        "partner_id.target_odoo_version_id",
        "module_id.wip_version_ids",
        "module_id.obsolete_version_id",
        # "task_ids.stage_id",
    )
    def _compute_migrated(self):
        versions = self.env["odoo.version"].search([])
        for record in self:
            target_version = record.partner_id.target_odoo_version_id
            if not target_version:
                record.migration_status = False
                continue
            if record.module_id.obsolete_version_id:
                obsolete_version_ids = versions.filtered(
                    lambda v: float(v.name)
                    >= float(record.module_id.obsolete_version_id.name)  # noqa: B023
                ).ids
            else:
                obsolete_version_ids = []
            if target_version in record.module_id.wip_version_ids:
                record.migration_status = "ongoing_pr"
            elif target_version.id in obsolete_version_ids:
                record.migration_status = "obsolete"
            elif target_version in record.module_id.available_version_ids:
                record.migration_status = "done"
            else:
                record.migration_status = False

    def open_pull_request(self):
        self.ensure_one()
        dest_module_version = self.env["module.version"].search(
            [
                ("version_id", "=", self.partner_id.target_odoo_version_id.id),
                ("url_pull_request", "!=", False),
                ("module_id", "=", self.module_id.id),
                ("state", "=", "pending"),
            ]
        )
        if not dest_module_version:
            raise exceptions.UserError(_("No known migration PR for this module."))
        client_action = {
            "type": "ir.actions.act_url",
            "name": "Migration PR",
            "target": "new",
            "url": dest_module_version.url_pull_request,
        }
        return client_action
