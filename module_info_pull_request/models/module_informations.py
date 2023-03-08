from odoo import api, fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    pr_ids = fields.Many2many("pull.request", string="Active Pull Request")
    pr_nbr = fields.Integer(compute="_compute_pr_nbr", string="# of Modules")

    @api.depends("pr_ids")
    def _compute_pr_nbr(self):
        for record in self:
            record.pr_nbr = len(record.pr_ids)
