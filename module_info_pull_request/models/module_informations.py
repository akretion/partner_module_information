from odoo import fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    module_id = fields.Many2one("pull.request", string="Active Pull Request")
