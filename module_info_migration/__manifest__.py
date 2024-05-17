{
    "name": "Module Info Migration",
    "description": "Show information about work still to do for migration for partners",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/partner-module-information",
    "category": "Tools",
    "depends": ["module_info_partner", "project", "project_stage_state"],
    "data": [
        "views/res_partner.xml",
        "views/module_partner.xml",
        "views/module_information.xml",
        # "wizard/module_task_creator.xml",
    ],
    "installable": True,
}
