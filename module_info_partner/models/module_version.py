# coding: utf-8

from odoo import models, fields, api


class ModuleVersion(models.Model):
    _name = "module.version"

    version_id = fields.Many2one("odoo.version", required=True, index=True)
    module_id = fields.Many2one("module.information", required=True, index=True)
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")],
        default="pending",
        help="Indicates if module is available or has to be migrated.",
    )
    url_pull_request = fields.Char(
        help="URL of the ongoing pull request for the module migration"
    )

    _sql_constraints = [
        (
            "module_version_uniq",
            "unique(module_id, version_id)",
            "Not possible to have twice the same module for the same version!",
        )
    ]
