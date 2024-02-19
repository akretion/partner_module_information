from odoo import fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    obsolete_version_id = fields.Many2one(
        "odoo.version",
        string="Obsolete Version",
        help=(
            "The version indicated here and all version after that will be "
            "considered obsolete. The migration status will take it into account"
        ),
    )
