from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    module_partner_ids = fields.Many2many('module.partner', string="Modules")
