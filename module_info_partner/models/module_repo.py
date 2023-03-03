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
    module_ids_nbr = fields.Integer(
        compute="_compute_module_ids_nbr", string="# of Modules"
    )

    @api.depends("module_ids")
    def _compute_module_ids_nbr(self):
        for record in self:
            record.module_ids_nbr = len(record.module_ids)
