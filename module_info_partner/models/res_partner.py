from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    module_auth_api_key_id = fields.Many2one("auth.api.key", string="Module API KEY")
    version_id = fields.Many2one("odoo.version", string="Current Odoo version")
    current_pr_nbr = fields.Integer(compute="_compute_current_pr_nbr")
    higher_pr_nbr = fields.Integer(compute="_compute_higher_pr_nbr")

    def _compute_current_pr_nbr(self):
        for record in self:
            record.current_pr_nbr = self.env["pull.request"].search_count(
                [
                    ("module_ids.partner_id", "=", record.id),
                    ("version_id", "=", record.version_id.id),
                ]
            )

    def _compute_higher_pr_nbr(self):
        for record in self:
            record.higher_pr_nbr = self.env["pull.request"].search_count(
                [
                    ("module_ids.partner_id", "=", record.id),
                    ("version_id.name", ">", record.version_id.name),
                ]
            )
