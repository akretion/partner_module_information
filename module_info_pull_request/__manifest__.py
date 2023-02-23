{
    "name": "Module Info Pull Request",
    "summary": "Information about Pull Request state on modules",
    "version": "14.0.0.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/partner-module-information",
    "category": "Tools",
    "depends": ["queue_job", "module_info_partner"],
    "data": [
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
        "views/pull_request.xml",
        "security/ir.model.access.csv",
        "views/module_information.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["pyyaml"]},
}
