import logging

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _inherit = "pull.request"

    def _domain_project_id(self):
        domain = [("allow_timesheets", "=", True)]
        if not self.user_has_groups("hr_timesheet.group_timesheet_manager"):
            return expression.AND(
                [
                    domain,
                    [
                        "|",
                        ("privacy_visibility", "!=", "followers"),
                        ("allowed_internal_user_ids", "in", self.env.user.ids),
                    ],
                ]
            )
        return domain

    timesheet_ids = fields.One2many("account.analytic.line", "pr_id", "Timesheets")
    project_id = fields.Many2one(
        "project.project",
        "Project",
        compute="_compute_project_id",
        store=True,
        readonly=False,
        domain=_domain_project_id,
    )
    task_id = fields.Many2one(
        "project.task",
        "Task",
        compute="_compute_task_id",
        store=True,
        readonly=False,
        index=True,
        domain="["
        "('project_id.allow_timesheets', '=', True), "
        "('project_id', '=?', project_id)]",
    )

    @api.depends("task_id", "task_id.project_id")
    def _compute_project_id(self):
        for line in self.filtered(lambda line: not line.project_id):
            line.project_id = line.task_id.project_id

    @api.depends("project_id")
    def _compute_task_id(self):
        for line in self.filtered(lambda line: not line.project_id):
            line.task_id = False
