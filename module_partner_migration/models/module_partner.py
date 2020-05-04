# coding: utf-8

from odoo import models, fields, api


class ModulePartner(models.Model):
    _inherit = "module.partner"

    migration_status = fields.Selection(
        selection=[
            ('wip', 'Work In Progress'),
            ('obsolete', 'Obsolete'),
            ('ongoing_pr', 'Ongoing Pull Request'),
            ('done', 'Done'),
        ], compute="_compute_migrated", store=True)
    task_ids = fields.Many2many('project.task', string="tasks")

    @api.depends("module_id.available_version_ids", "partner_id.target_odoo_version_id", "module_id.wip_version_ids", "module_id.obsolete_version_id")
    def _compute_migrated(self):
        versions = self.env['odoo.version'].search([])
        for record in self:
            target_version = record.partner_id.target_odoo_version_id
            if not target_version:
                continue
            if record.module_id.obsolete_version_id:
                obsolete_version_ids = versions.filtered(lambda v: float(v.version) >= float(record.module_id.obsolete_version_id.version)).ids
            else:
                obsolete_version_ids = []
            # it does not matter if module is migrated, if task are linked
            # there is still work to do...?
            # TODO FIXME need to check state of task to see if done or not.
            # need to check the right solution...boolean on the task step??
            if record.task_ids:
                record.migration_status = 'wip'
            elif target_version.id in obsolete_version_ids:
                record.migration_status = 'obsolete'
            # FIXME we consider no version at all as a native odoo module because
            # for now, they have no version. And any other known module should have
            # at least one version. But this is just temporary, as it does not seem
            # very reliable
            elif target_version in record.module_id.available_version_ids:
                record.migration_status = 'done'
            elif target_version in record.module_id.wip_version_ids:
                record.migration_status = 'ongoing_pr'
