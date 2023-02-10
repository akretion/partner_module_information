from odoo import fields, models


class ModuleRepo(models.Model):
    _name = "module.repo"
    _rec_name = "name"
    _description = "List of all module repository"

    name = fields.Char(string="Repository Name", readonly=True, index=True)
    organization = fields.Char(string="Organization Name")
    url = fields.Char()
    modules_ids = fields.One2many(
        "module.information", "repo_id", string="Module information"
    )
