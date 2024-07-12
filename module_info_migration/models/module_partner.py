from odoo import api, fields, models


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
