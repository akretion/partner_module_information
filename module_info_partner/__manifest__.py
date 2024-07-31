{
    "name": "Module Info Partner",
    "summary": "Information about odoo modules used by your partners",
    "version": "16.0.0.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/partner-module-information",
    "category": "Tools",
    "depends": ["fastapi", "auth_api_key"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "views/module_information.xml",
        "views/res_partner.xml",
        "data/odoo_version.xml",
        "data/res_users.xml",
        "data/fastapi_endpoint.xml",
        "views/module_partner.xml",
        "views/module_version.xml",
        "views/module_repo.xml",
    ],
    "installable": True,
}
