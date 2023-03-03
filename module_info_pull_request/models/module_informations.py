from odoo import api, fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    pr_ids = fields.Many2many("pull.request", string="Active Pull Request")
    pr_ids_nbr = fields.Integer(compute="_compute_pr_ids_nbr", string="# of Modules")

    @api.depends("pr_ids")
    def _compute_pr_ids_nbr(self):
        for record in self:
            record.pr_ids_nbr = len(record.pr_ids)

    def action_view_pr(self):
        self.ensure_one()
        prs = self.mapped("pr_ids")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "module_info_pull_request.pull_request_action"
        )
        if len(prs) > 0:
            action["domain"] = [("id", "in", prs.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
