from odoo import api, fields, models


class ModuleRepo(models.Model):
    _name = "module.repo"
    _rec_name = "name"
    _description = "List of all module repository"

    name = fields.Char(string="Repository Name", index=True)
    organization = fields.Char(string="Organization Name")
    url = fields.Char()
    module_ids = fields.One2many(
        "module.information", "repo_id", string="Module information"
    )
    module_nbr = fields.Integer(compute="_compute_module_nbr", string="# of Modules")

    _sql_constraints = [
        (
            "uniq_orga_repo",
            "unique(name, organization)",
            "the pair repo name and organization must be unique",
        )
    ]

    @api.depends("module_ids")
    def _compute_module_nbr(self):
        for record in self:
            record.module_nbr = len(record.module_ids)
