from odoo import models, fields, api


class HostRepository(models.Model):
    _name = "host.repository"
    _rec_name = 'repo_name'
    _description = "List of all module repository"

    repo_name = fields.Char(string="Repository Name", readonly=True, index=True)
    url = fields.Char()
    modules_ids = fields.One2many("module.information",
                                  "host_repository_id",
                                  string="Module information")
    # will be populate with adaptation of module_info_import


class ModuleInformation(models.Model):
    _name = "module.information"
    _rec_name = 'technical_name'
    _description = "Module Information and availability"

    # TODO add unique constraint, see proposal line 69
    technical_name = fields.Char(string="Technical Name", readonly=True, index=True)
    name = fields.Char(readonly=True)
    description_rst = fields.Text(readonly=True)
    description_html = fields.Html(readonly=True)
    short_description = fields.Text(
        help="Edit this field to store complementary information about the " "module"
    )
    authors = fields.Char(readonly=True)
    host_repository_id = fields.Many2one("host.repository", index=True, string="Host Repository")
    module_version_ids = fields.One2many(
        "module.version", "module_id", string="Module Versions"
    )
    available_version_ids = fields.Many2many(
        "odoo.version",
        "available_module_version_rel",
        "module_id",
        "version_id",
        string="Available Odoo Versions",
        compute="_compute_version_ids",
        store=True,
    )
    wip_version_ids = fields.Many2many(
        "odoo.version",
        "wip_module_version_rel",
        "module_id",
        "version_id",
        string="Work in Progress Versions",
        compute="_compute_version_ids",
        store=True,
    )
    equivalent_module_ids = fields.Many2many(
        "module.information",
        "equivalent_module_info_rel",
        "module1_id",
        "module2_id",
        help="Fill the field with modules that replace or are replaced by "
        "this one. (splitted module or renamed...)",
    )
    alternative_module_ids = fields.Many2many(
        "module.information",
        "alternative_module_info_rel",
        "module1_id",
        "module2_id",
        help="Fill the field with modules that have very similar features with"
        "this one and could replace it.",
    )
    
    # TO VALIDATE: (cf anotation add unique constraint)
    _sql_constraints = [
        ('uniq_technical_name', 'unique(technical_name)', 'technical_name must be unique'),
    ]

    @api.depends(
        "module_version_ids.state", "equivalent_module_ids.module_version_ids.state"
    )
    def _compute_version_ids(self):
        # TODO for now, it does not take alternative_module_ids into account
        # not sure if it should.
        # more importantly, it seems very hard to take all case into account.
        # For instance, if a module is renamed at every version, it will
        # have multiple equivalent modules. But it also could have multiple
        # equivalent modules if it has been splitted. renamed and splitted...

        # for now, we manage most case and don't care too much about
        # the very special cases.
        # we check if every module version of equivalent modules are done.
        odoo_versions = self.env['odoo.version'].search([])
        for module in self:
            available_version_ids = []
            wip_version_ids = []
            for module_version in module.module_version_ids:
                if module_version.state == "done":
                    available_version_ids.append(module_version.version_id.id)
                elif module_version.state == 'pending':
                    wip_version_ids.append(module_version.version_id.id)
            missing_versions = odoo_versions.filtered(lambda v: v.id not in available_version_ids and v.id not in wip_version_ids)
            for missing_version in missing_versions:
                equivalent_modules = module._get_equivalent_modules_from_version(missing_version)
                if not equivalent_modules:
                    continue
                equivalent_module_versions = self.env["module.version"].search(
                    [
                        ("module_id", "in", equivalent_modules.ids),
                        ("version_id", "=", missing_version.id),
                    ]
                )
                if len(equivalent_module_versions) == len(equivalent_modules):
                    if all([mv.state == 'done' for mv in equivalent_module_versions]):
                        available_version_ids.append(missing_version.id)
                    else:
                        wip_version_ids.append(missing_version.id)

            module.available_version_ids = available_version_ids
            module.wip_version_ids = wip_version_ids

    def _get_equivalent_modules_from_version(self, version):
        self.ensure_one()
        return self.equivalent_module_ids
