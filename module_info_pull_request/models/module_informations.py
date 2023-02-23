from odoo import fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    pr_ids = fields.Many2many("pull.request", string="Active Pull Request")
