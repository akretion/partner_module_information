# coding: utf-8

from odoo import models, fields, api


class ModuleInformation(models.Model):
    _name = "module.information"

    # TODO add unique constraint
    technical_name = fields.Char(string="Technical Name", readonly=True, index=True)
    name = fields.Char(readonly=True)
    description_rst = fields.Text(readonly=True)
    description_html = fields.Html(readonly=True)
    short_description = fields.Text(
        help="Edit this field to store complementary information about the " "module"
    )
    authors = fields.Char(readonly=True)
    module_version_ids = fields.One2many(
        "module.version", "module_id", string="Module Versions"
    )
    available_version_ids = fields.Many2many(
        "odoo.version",
        string="Available Odoo Versions",
        compute="_compute_available_version_ids",
        store=True,
    )
    equivalent_module_ids = fields.Many2many(
        "module.information",
        "equivalent_module_info_rel",
        "module1",
        "module2",
        help="Fill the field with modules that replace or are replaced by "
        "this one. (splitted module or renamed...)",
    )
    alternative_module_ids = fields.Many2many(
        "module.information",
        "alternative_module_info_rel",
        "module1",
        "module2",
        help="Fill the field with modules that have very similar features with"
        "this one and could replace it.",
    )

    @api.depends(
        "module_version_ids.state", "equivalent_module_ids.module_version_ids.state"
    )
    def _compute_available_version_ids(self):
        # TODO for now, it does not take alternative_module_ids into account
        # not sure if it should.
        # more importantly, it seems very hard to take all case into account.
        # For instance, if a module is renamed at every version, it will
        # have multiple equivalent modules. But it also could have multiple
        # equivalent modules if it has been splitted. renamed and splitted...

        # for now, we manage most case and don't care too much about
        # the very special cases.
        # we check if every module version of equivalent modules are done.
        for module in self:
            version_ids = []
            for module_version in module.module_version_ids:
                if module_version.state == "done":
                    version_ids.append(module_version.version_id.id)

            # if there are equivalent modules, check if they are available
            # but only for our module's not available versions.
            equivalent_module_versions = self.env["module.version"].search(
                [
                    ("module_id", "in", module.equivalent_module_ids.ids),
                    ("version_id", "not in", version_ids),
                ]
            )
            pending_versions = equivalent_module_versions.filtered(
                lambda v: v.state == "pending"
            )
            done_versions = equivalent_module_versions.filtered(
                lambda v: v.state == "done"
            )
            # if for one version we have done and pending, we consider the
            # module has been split and both should be done to be available
            available = list(
                set(done_versions.mapped("version_id").ids)
                - set(pending_versions.mapped("version_id").ids)
            )
            version_ids = available + version_ids
            for eq_module_version in equivalent_module_versions:
                pass

            module.available_version_ids = version_ids
