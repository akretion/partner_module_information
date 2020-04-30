# coding: utf-8

from odoo import models, fields, api


class ModulePartner(models.Model):
    _inherit = "module.partner"

    # simple boolean for nw, but it maybe it should be a state to show if it started
    # (if there is a git PR for instance) or even consider a PR as migrated...
    # we make this extra simple for now
    migrated = fields.Boolean(compute="_compute_migrated", store=True)

    @api.depends("module_id.available_version_ids", "partner_id.target_odoo_version_id")
    def _compute_migrated(self):
        for record in self:
            target_version = record.partner_id.target_odoo_version_id
            if not target_version:
                continue
            # FIXME we consider no version at all as a native odoo module because
            # for now, they have no version. And any other known module should have
            # at least one version. But this is just temporary, as it does not seem
            # very reliable
            if (
                not record.module_id.available_version_ids
                or target_version in record.module_id.available_version_ids
            ):
                record.migrated = True
            else:
                record.migrated = False
