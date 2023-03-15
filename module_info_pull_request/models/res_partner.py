from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    current_pr_nbr = fields.Integer(compute="_compute_current_pr_nbr")
    higher_pr_nbr = fields.Integer(compute="_compute_higher_pr_nbr")
    module_nbr = fields.Integer(compute="_compute_module_nbr")

    def _get_domain_current_pr(self):
        return [
            ("module_ids.module_partner_ids.partner_id", "=", self.id),
            ("version_id", "=", self.version_id.id),
        ]

    def _get_domain_higher_pr(self):
        return [
            ("module_ids.module_partner_ids.partner_id", "=", self.id),
            ("version_id", ">", self.version_id.id),
        ]

    def _compute_current_pr_nbr(self):
        for record in self:
            record.current_pr_nbr = self.env["pull.request"].search_count(
                record._get_domain_current_pr()
            )

    def _compute_higher_pr_nbr(self):
        for record in self:
            record.higher_pr_nbr = self.env["pull.request"].search_count(
                record._get_domain_higher_pr()
            )

    def get_action_pr_tree_current(self):
        prs = self.env["pull.request"].search(self._get_domain_current_pr())

        current_pr = prs.mapped("id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "pull.request",
            "name": f"Current Pull Request for {self.name}",
            "views": [
                [
                    self.env.ref("module_info_pull_request.pull_request_tree_view").id,
                    "tree",
                ]
            ],
            "view_mode": "tree,form",
            "domain": [["id", "in", current_pr]],
        }

    def get_action_pr_tree_higher(self):
        prs = self.env["pull.request"].search(self._get_domain_higher_pr())
        current_pr = prs.mapped("id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "pull.request",
            "name": f"Higher version Pull Request for {self.name}",
            "views": [
                [
                    self.env.ref("module_info_pull_request.pull_request_tree_view").id,
                    "tree",
                ]
            ],
            "view_mode": "tree,form",
            "domain": [["id", "in", current_pr]],
        }

    def _get_domain_module(self):
        return [("partner_id", "=", self.id)]

    def _compute_module_nbr(self):
        for record in self:
            record.module_nbr = self.env["module.partner"].search_count(
                record._get_domain_module()
            )

    def get_action_module_partner_tree(self):
        modules = self.env["module.partner"].search(self._get_domain_module())
        modules = modules.mapped("id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "module.partner",
            "name": f"Modules used by {self.name}",
            "views": [
                [
                    self.env.ref("module_info_partner.module_partner_tree_view").id,
                    "tree",
                ]
            ],
            "view_mode": "tree,form",
            "domain": [["id", "in", modules]],
        }
