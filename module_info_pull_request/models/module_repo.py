from odoo import fields, models


class ModuleRepo(models.Model):
    _inherit = "module.repo"

    updated_at = fields.Datetime(string="Last Update")
